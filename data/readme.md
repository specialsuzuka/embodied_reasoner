- `train_muliturn_9390.json`: training data with sharegpt format
    ``` json
        [
            {
                "messages":[
                    {"role":"system", "content":"xxx"},
                    {"role":"user", "content":"<image>xxx"},
                    {"role": "assistant", "content": "xxx"},
                    ...
                ]
                "images":[
                    "",
                    ...
                ]
            }
        ]
    ```
- `agent_positions.json` : Simulator navigation failed, some navigation points were manually set to support evaluation
- `test_809.json`: 809 test data