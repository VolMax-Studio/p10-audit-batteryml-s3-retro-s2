import P10Core.Model.AdjudicationAutomaton

open P10Core.Model.AdjudicationAutomaton

def replayDecisionView : DecisionView := {
  protocolFault := none,
  falsifiable := true,
  obligations := [
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.violated,
    EvalStatus.satisfied
  ],
  hasBlockingLimitation := false,
  hasNonBlockingLimitation := true,
  admissibleNovelFinding := false
}

def main : IO Unit := do
  let outcome := adjudicate replayDecisionView
  match outcome with
  | TerminalOutcome.protocolError err =>
    IO.println s!"TERMINAL_OUTCOME: PROTOCOL_ERROR ({repr err})"
  | TerminalOutcome.verdict v =>
    IO.println s!"TERMINAL_OUTCOME: VERDICT ({repr v})"
