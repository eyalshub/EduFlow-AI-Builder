#app/schemas/input_model.py
from typing import Optional, List, Literal
from pydantic import BaseModel, model_validator


class Stage1Input(BaseModel):
    topicName: str  # Course topic
    subject: str  # Discipline
    gradeLevel: str  # Age / Grade level

    bigIdea: str  # Big Idea
    learningGate: Literal['Meeting Gate', 'Independence Gate', 'Discovery Gate']  # Learning Gate
    skills: List[str]  # Skills

    context: Optional[str] = None  # Previous lesson context
    freePrompt: Optional[str] = None  # Free prompt
    courseLanguage: Optional[str] = "he"  # Course language

    generationScope: Optional[Literal["Single Lesson", "Full Course"]] = "Single Lesson"
    numLessons: Optional[int] = None  # Only needed for Full Course
    usePerplexity: Optional[bool] = False  #
    @model_validator(mode='after')
    def validate_num_lessons(self) -> 'Stage1Input':
        if self.generationScope == "Full Course" and not self.numLessons:
            raise ValueError("numLessons must be provided when generationScope is 'Full Course'")
        return self


class LessonContentAgentInput(BaseModel):
    topicName: str
    gradeLevel: str
    bigIdea: str
    lessonTitle: str
    lessonIndex: int
    pedagogicalProfile: dict