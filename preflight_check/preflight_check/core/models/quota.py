from dataclasses import dataclass


@dataclass
class UsageQuotaLimit:
    """Represents an Azure usage quota limit"""

    name: str
    display_name: str
    limit: int
    usage: int
