from enum import Enum

class CodeChallengeJudgmentJobStatus(Enum):
    """
    Description:
        CodeChallengeJudgmentJob 엔티티의 status 필드를 정의하는 enum 클래스
    """
    READY = "ready"
    IN_PROGRESS = "in progress"
    COMPLETE = "complete"
    STOPPED = "stopped"
