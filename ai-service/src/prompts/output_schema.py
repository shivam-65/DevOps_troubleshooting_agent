OUTPUT_SCHEMA = """{
  "summary": "string - Brief summary of the investigation findings (2-3 sentences)",
  "rootCause": "string - Detailed explanation of the root cause with evidence references",
  "confidence": "number - Confidence score between 0.0 and 1.0",
  "reasoning": "string - Step-by-step reasoning that led to the conclusion",
  "recommendedActions": [
    {
      "type": "string - One of: RESTART_SERVICE, SCALE_UP, ROLLBACK_DEPLOYMENT, RUN_SCRIPT, APPLY_CONFIG_CHANGE, CLEAR_CACHE, FAILOVER, CUSTOM",
      "title": "string - Short action title",
      "description": "string - Detailed description of what this action does",
      "command": "string or null - Specific command to execute (if applicable)",
      "targetService": "string or null - Service this action targets",
      "parameters": "object or null - Additional parameters for the action",
      "risk": "string - One of: LOW, MEDIUM, HIGH",
      "estimatedImpact": "string - Expected outcome of this action"
    }
  ]
}"""
