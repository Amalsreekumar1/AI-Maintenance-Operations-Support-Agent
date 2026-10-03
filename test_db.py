from huggingface_hub import HfApi

api = HfApi()

print("Datasets by nick007x:")
for d in api.list_datasets(author="nick007x"):
    print(" -", d.id)

for repo in ["nick007x/eevblog-posts", "nick007x/eevblog-forum-data"]:
    try:
        api.dataset_info(repo)
        print("OK:", repo)
    except Exception as e:
        print("FAIL:", repo, "-", type(e).__name__)