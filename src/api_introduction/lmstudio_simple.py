import lmstudio as lms
model = lms.llm()
print(model.respond("Sally is 77, Bill is 32, and Alex is 44 years old. Pairwise, what are their age differences? Print results in JSON format. Be concise and only provide a correct answer, no need to think about different correct answers."))
