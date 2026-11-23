"""Pydantic data models shared by the whole app."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Difficulty = Literal["easy", "medium", "hard"]
QuestionType = Literal["mcq", "short", "exercise"]


class Question(BaseModel):
    topic: str
    difficulty: Difficulty
    type: QuestionType
    question: str = Field(min_length=1)
    options: list[str] = Field(default_factory=list)

    # MCQ answers are resolved from answer_index.
    # Short/exercise questions still use answer text.
    answer: str = ""
    answer_index: int | None = Field(default=None, ge=0, le=3)

    rubric: list[str] = Field(default_factory=list)
    source_page: int = 1

    @field_validator("difficulty", "type", mode="before")
    @classmethod
    def _lowercase(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @model_validator(mode="before")
    @classmethod
    def _resolve_mcq_answer(cls, data):
        if not isinstance(data, dict):
            return data

        data = dict(data)

        if str(data.get("type", "")).strip().lower() == "mcq":
            options = data.get("options") or []
            index = data.get("answer_index")

            if index is not None:
                try:
                    index = int(index)
                except (TypeError, ValueError):
                    raise ValueError("MCQ answer_index must be an integer")

                if not 0 <= index < len(options):
                    raise ValueError(
                        "MCQ answer_index must point to an existing option"
                    )

                # Python selects the exact option text.
                data["answer"] = options[index]

        return data

    @model_validator(mode="after")
    def _check_consistency(self):
        if self.type == "mcq":

            if len(self.options) != 4:
                raise ValueError(
                    "An MCQ question must have exactly 4 options"
                )

            normalized_options = [
                option.strip().casefold()
                for option in self.options
            ]

            if len(set(normalized_options)) != 4:
                raise ValueError(
                    "MCQ options must be unique"
                )

            if not self.answer.strip():
                raise ValueError(
                    "MCQ must have a valid correct answer"
                )

            matched = None

            for option in self.options:
                if option.strip().casefold() == self.answer.strip().casefold():
                    matched = option
                    break

            if matched is None:
                raise ValueError(
                    "The MCQ answer must match one of the options"
                )

            self.answer = matched

            if not self.rubric:
                self.rubric = ["Chooses the correct option"]

        else:
            if not self.answer.strip():
                raise ValueError(
                    "Short and exercise questions need an answer"
                )

            if not self.rubric:
                self.rubric = [self.answer]

        return self


class QuestionSet(BaseModel):
    questions: list[Question] = Field(min_length=1)


class RubricCheck(BaseModel):
    point: str
    covered: bool


class RubricJudgement(BaseModel):
    """What the LLM returns when it marks an answer."""

    checks: list[RubricCheck]
    feedback: str


class GradeResult(BaseModel):
    """The final mark that the app shows and stores."""

    points: int
    max_points: int
    score: float  # points / max_points, between 0 and 1
    checks: list[RubricCheck]
    feedback: str

    @property
    def missing_points(self) -> list[str]:
        return [check.point for check in self.checks if not check.covered]