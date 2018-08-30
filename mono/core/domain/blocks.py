from typing import List
from dataclasses import dataclass, field


@dataclass
class Block:
    main: List[str]
    side: List[str] = field(default_factory=list)
    side_offset: int = 0
    block_offset: int = 1
