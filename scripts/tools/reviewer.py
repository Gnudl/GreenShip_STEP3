"""CLI Runner cho AI-Agent Reviewer - GreenShip STEP 2."""

import sys
from pathlib import Path

# Thêm thư mục src vào sys.path
THU_MUC_GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(THU_MUC_GOC / "src"))

from ai_agent_reviewer import GreenShipReviewerAgent, main

if __name__ == "__main__":
    main()
