import random
import re
import threading
import time
from typing import Dict, Iterable, List, Optional

from mathgen.math.precise_num import PN

from ..math.evaluate import evaluate_expression
from .mathproblem import (
    MathProblem,
    MathProblemFormat,
    MathProblemModel,
    split_prefix,
)

ANSWER_FORMATS: Dict[MathProblemFormat, re.Pattern] = {
    "number": re.compile(r"^\$-?\d+\$$"),
    "decimal": re.compile(r"^\$-?\d*\.\d+\$$"),
    "fraction": re.compile(r"^\$-?\\frac{\d+}{\d+}\$$"),
    "mixed": re.compile(r"^\$-?\d+\\frac{\d+}{\d+}\$$")
}

def recognize_answer_format(answer: str) -> MathProblemFormat:
    for format, regex in ANSWER_FORMATS.items():
        if regex.match(answer):
            return format
    raise ValueError(f"Didn't find matching answer format for: {repr(answer)}")

QA_GLOBALS = {
    "text": lambda x: rf"\text{{{x}}}",
    "blank": r"$\underline{\qquad}$",
}

class MathProblemGenerator:
    MAX_TRIES = 50

    def __init__(self, model: MathProblemModel, seed=None):
        self.model = model
        self.seed = seed
        self.__current_seed = seed
        self.__generate_lock = threading.Lock()

    def _generate(self) -> MathProblem:
        for _ in range(self.MAX_TRIES):
            self.vars = {}
            self.questions = set()
            self.problem = MathProblem(name=self.model.name, format=self.model.format, units=self.model.units, rtl=self.model.rtl)
            for line in self.model.code.splitlines():
                line = line.strip()
                if not line:
                    continue
                prefix_line = split_prefix(line)
                assert prefix_line is not None
                prefix, line = prefix_line
                if getattr(self, f"_gen_{prefix}")(line) == False:
                    break
                self._step_current_seed()
            else:
                if self.questions:
                    self.problem.question = random.Random(self.__current_seed).choice(list(self.questions))
                self._step_current_seed()
                if self.problem.format == "multiplechoice":
                    self._finalize_choices()
                return self.problem
        raise RuntimeError(f"Failed to generate a valid problem for {self.model.name}")

    def generate(self) -> MathProblem:
        with self.__generate_lock:
            problem = self._generate()
        return problem

    def _gen_var(self, line: str):
        name, expr = line.split("=", 1)
        self.vars[name.strip()] = evaluate_expression(
            expr.strip(), vars={**QA_GLOBALS, **self.vars}, seed=self.__current_seed
        )

    def _gen_condition(self, line: str):
        return evaluate_expression(
            line.strip(), vars=self.vars, seed=self.__current_seed
        )

    def _gen_question(self, line: str):
        if "'" in line:
            raise ValueError("Single quotes are not allowed in questions")
        self.questions.add(evaluate_expression(f"f{repr("$" + line.strip() + "$")}", {**QA_GLOBALS, **self.vars}, seed=self.__current_seed))
    
    def _gen_textquestion(self, line: str):
        if "'" in line:
            raise ValueError("Single quotes are not allowed in questions")
        self.questions.add(evaluate_expression(f"f{repr(line.strip())}", {**QA_GLOBALS, **self.vars}, seed=self.__current_seed))

    def _gen_answer(self, line: str):
        if "'" in line:
            raise ValueError("Single quotes are not allowed in answers")
        self.problem.answer = evaluate_expression(f"f{repr("$" + line.strip() + "$")}", {**QA_GLOBALS, **self.vars}, seed=self.__current_seed)
        if self.problem.format == "auto":
            self.problem.format = recognize_answer_format(self.problem.answer)

    def _gen_choices(self, line: str):
        if "'" in line:
            raise ValueError("Single quotes are not allowed in choices")
        if self.problem.format != "multiplechoice":
            raise ValueError("Choices are only allowed for multiple choice questions")
        
        if self.problem.choices is None:
            self.problem.choices = []
        results = evaluate_expression(
            line.strip(), {**QA_GLOBALS, **self.vars}, seed=self.__current_seed
        )
        if not isinstance(results, Iterable):
            results = [results]
        results = [f"${x}$" for x in results]
        self.problem.choices.extend(results)
    
    def _gen_numchoices(self, line: str):
        if self.problem.format != "multiplechoice":
            raise ValueError("Numchoices is only allowed for multiple choice questions")
        result = evaluate_expression(
            line.strip(), vars=self.vars, seed=self.__current_seed
        )
        if not isinstance(result, PN) or not result.is_integer:
            raise ValueError("Numchoices must be an integer")
        if not (2 <= result <= 5):
            raise ValueError("Numchoices must be between 2 and 5")
        self.problem.numchoices = result.num

    def _gen_order(self, line: str):
        if self.problem.format != "multiplechoice":
            raise ValueError("Choices are only allowed for multiple choice questions")
        results = evaluate_expression(
            line.strip(), vars=self.vars, seed=self.__current_seed
        )
        if not isinstance(results, Iterable):
            results = [results]
        results = [f"${x}$" for x in results]
        self.problem.order = results

    def _gen_key(self, line: str):
        self.problem.key = evaluate_expression(
            line.strip(), vars=self.vars, seed=self.__current_seed
        )
        if not isinstance(self.problem.key, list):
            raise ValueError("Key must be a list")
        if len(self.problem.key) < 2: 
            raise ValueError("Key must have at least 2 elements")
        if not isinstance(self.problem.key[0], str):
            raise ValueError("Key index 0 must be a string")

    def _gen_units(self, line: str):
        if "'" in line:
            raise ValueError("Single quotes are not allowed in units")
        self.problem.units = evaluate_expression(f"f{repr(line.strip())}", {**QA_GLOBALS, **self.vars}, seed=self.__current_seed)

    def _gen_group(self, line: str):
        raise Exception("Group directive not handled by mathgen core")

    def _step_current_seed(self):
        if isinstance(self.__current_seed, int):
            self.__current_seed = (
                self.__current_seed**2 * 3041 + self.__current_seed * 1009
            ) % 1000000007

    def _finalize_choices(self):
        if self.problem.choices is None:
            raise ValueError("Choices are required for multiple choice questions")
        unique_choices = list(set(self.problem.choices))
        unique_choices = [x for x in unique_choices if x != self.problem.answer]
        numchoices = (self.problem.numchoices or 5) - 1
        if len(unique_choices) < numchoices:
            raise ValueError("Not enough unique choices")
        
        final_choices = random.Random(self.__current_seed).sample(unique_choices, numchoices)
        self._step_current_seed()
        
        answer_index = random.Random(self.__current_seed).randrange(numchoices + 1)
        self._step_current_seed()

        final_choices.insert(answer_index, self.problem.answer)

        if self.problem.order:
            if missing_choice := next((x for x in final_choices if x not in self.problem.order), None):
                raise ValueError(f"Choice {missing_choice} missing from choice order")
            final_choices = [x for x in self.problem.order if x in final_choices]
            answer_index = final_choices.index(self.problem.answer)

        self.problem.choices = final_choices
        self.problem.answer = chr(ord("A") + answer_index)
    
    @staticmethod
    def generate_multiple(models: List[MathProblemModel], amount: int, seed: Optional[int] = None):
        if seed is None:
            seed = time.time_ns() % 2**32
        
        rng = random.Random(seed)
        generators = {model.name: MathProblemGenerator(model, seed + i) for i, model in enumerate(models)}
        names = [model.name for model in models]

        problems: List[MathProblem] = []
        failures = 0
        while len(problems) < amount:
            if failures == 0 or failures > 10:
                name = rng.choice(names)
            problem = generators[name].generate()
            
            if failures == 60:
                raise RuntimeError(f"Reached failure threshold for model list generation {names}")
            
            problems_to_check = problems
            if failures >= 20:
                if failures >= 50 or len(problems) < 10:
                    problems_to_check = problems[-2:]
                else:
                    cutoff = (len(problems) - 5) // 5 * 5
                    problems_to_check = (p for i, p in enumerate(problems) if i >= cutoff)
            
            if any(problem.key == p.key for p in problems_to_check if problem.key and p.key):
                failures += 1
                continue
            failures = 0
            
            problems.append(problem)
            if len(problems) % (amount // 3) == 0:
                print(f"Generated {len(problems)} out of {amount} problems")
        
        return problems

# poetry run python -m src.mathgen.gen.generate
if __name__ == "__main__":
    model = MathProblemModel(
        id="test",
        code="\n".join(
            [
                "@var a = rand(3, 100) / rand(3, 10)",
                "@var b = rand(3, 100) / rand(3, 10)",
                "@condition a < 10 and b < 10 and is_improper(a, b)",
                "@question {a} \\times {b}?",
                "@answer {a * b}",
            ]
        ),
    )

    generator = MathProblemGenerator(model, seed=20)
    problem = generator.generate()
    print(problem.question)
    print(problem.answer)

    print(problem.model_dump_json())

    # print(generator.generate_multiple(5))
