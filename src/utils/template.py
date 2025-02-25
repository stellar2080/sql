extractor_template = """
You are an expert in the field of finance and database.
You need to follow the instructions below to solve the problem step by step:
1. Identify and extract any key entities from the text that can help with financial database queries
2. Format the answer in the same Python list format as the [Answer] part of the example
- When you have generated a list which already solves the problem, there is no need to generate more text

Example 1:
[Text]
Tell me all company names.
[Hint]
Here are some entity names for reference:
{{'China Construction Bank', 'China Mingsheng Bank', 'Securities Name'}}
[Answer]
['company names']
This list already solves the problem, so there is no need to continue generating text.

Example 2:
[Text]
I want to know the working capital and current ratio of Huaxia Bank.
[Hint]
Here are some entity names for reference:
{{'Total Assets', 'Working capital', 'Current ratio', 'current assets', 'return on assets'}}
[Answer]
['working capital','current ratio','Huaxia Bank']
This list already solves the problem, so there is no need to continue generating text.

Please start solving the problem:
[Text]
{}
"""

extractor_hint_template = """[Hint]
Here are some entity names for reference:
{}
"""

filter_template = """
You are an expert in the field of finance and database. 
You need to follow the instructions below to solve the problem step by step:
1. Select the tables and columns relevant to the question from the database schema
- When there is a column related to the organization code or name in the schema, select it
2. Format the answer in the same JSON format as the [Answer] part of the example
- The answer should only contain the selected tables and columns, and no other redundant information
- When you have generated a JSON statement which already solves the problem, there is no need to generate more text

Example:
[Schema]
=====
Table: Basic_Info
Column:
(Stk_Code; Comment: Securities code; Primary key)
(Stk_Name; Comment: Securities name; Sample: Huaxia Bank)
=====
Table: Balance_Sheet
Column:
(Stk_Code; Comment: Securities code; Foreign key: references Basic_Info(Stk_Code))
=====
Table: Income_Statement
Column:
(Stk_Code; Comment: Securities code; Foreign key: references Basic_Info(Stk_Code))
(Fee_Com_Inc; Comment: Fee and commission income)
(Fee_Com_Exp; Comment: Handling fees and commission expenses)
[Question]
What is the fee and commission income of Huaxia Bank?
[Answer]
{{
  "Basic_Info": ["Stk_Code","Stk_Name"],
  "Balance_Sheet": [],
  "Income_Statement": ["Stk_Code","Fee_Com_Inc"]
}}
This JSON statement already solves the problem, so there is no need to continue generating text.

Please start solving the problem:
[Schema]
{}
[Question]
{}
"""

filter_hint_template = """[Hint]
You can refer to following information:
{}
"""

# When generating SQL, we should always consider constraints:
# - In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
# - In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
# - If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
# - If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values


generator_template_p1 = """
You are an experienced financial database administrator.
You need to follow the instructions below to solve the problem step by step:
1. Based on the information given, think about which columns are needed to generate SQL
- When there is a column related to the organization code or name in the schema, the SQL statement you generate should select it
2. Consider and list the tables that contain the selected columns
3. Use the {} dialect to generate SQL statement
- Think carefully about whether you need to join tables, when joining tables, use alias like 't1,t2'
- When you have generated a SQL statement that already solves the problem, there is no need to generate more text

Please start solving the problem:
[Schema]
{}
[Question]
{}
"""

generator_hint_template = """[Hint]
You can refer to following information:
{}
"""

generator_template_p2 = """[Format]
The format of the SQL you generate should be the same as the following:
```sql

```
"""

reviser_template_p1 = """
You are an experienced financial database administrator.
You need to follow the instructions below to solve the problem step by step:
1. When executing {} SQL below, some errors occurred. Based on the information given, please fix up old SQL and generate correct SQL.
- When you have generated a SQL statement that already solves the problem, there is no need to generate more text

Please start solving the problem:
[Schema]
{}
[Question]
{}
"""

reviser_hint_template = """[Hint]
You can refer to following information:
{}
"""

reviser_template_p2 = """[Old SQL]
```sql
{}
```
[Error]
{}
[Format]
The format of the SQL you generate should be the same as the following:
```sql

```
"""
