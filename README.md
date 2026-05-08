# `squidfall`
A template for agent-native apps. For more information, [read the docs!](docs/README.md).

## Quickstart
**Step 1.** Clone the Squidfall GitHub repository. 
```bash
git clone https://github.com/deathlabs/squidfall.git
```

**Step 2.** Change directories to the folder downloaded.
```bash
cd squidfall
```

**Step 3.** Then, build Squidfall locally using the provided Makefile. 
```bash
make
```

**Step 4.** Save your environment variables (e.g., OpenAI API key) to a file called `.env` in the `inference` folder. 
```bash
echo "export OPENAI_API_KEY='AAA...'" > inference/.env
```

**Step 5.** Start Squidfall using the provided Makefile. 
```bash
make start
```
