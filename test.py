from evaluate import load
import os



# os.environ["CUDA_VISIBLE_DEVICES"] = "1"
## we need to set the model on cpu to debug
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


bertscore = load("bertscore")
predictions = ["hello world", "general kenobi"]
references = ["hello world", "general kenobi"]
# results = bertscore.compute(predictions=predictions, references=references, model_type="bert-base-uncased")
results = bertscore.compute(predictions=predictions, references=references, model_type="microsoft/codereviewer")
print(results)
