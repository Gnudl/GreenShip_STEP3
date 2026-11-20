"""CLI Runner cho AI-Agent Reporter - GreenShip STEP 2."""

import sys
from pathlib import Path

THU_MUC_GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(THU_MUC_GOC / "src"))

from ai_agent_reporter import GreenShipReporterAgent, main

if __name__ == "__main__":
    main()
