extractor_template = """
You are an expert in the field of finance and database.
You need to follow the instructions below to solve the problem step by step:
1. Identify and extract any key entities from the text that can help with financial database queries
2. Format the answer in the same Python list format as the [Answer] part of the example

Requirements:
When you have generated a list which already solves the problem, there is no need to generate more text

Example:
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
2. Format the answer in the same JSON format as the [Answer] part of the example

Requirements:
1. When there is column related to the organization name in the schema, select it
2. When you have generated a JSON statement which already solves the problem, there is no need to generate more text

Example:
[Schema]
=====
Table: Basic_Info
Column:
(Stk_Code, Comment: Securities code, Primary key)
(Stk_Name, Comment: Securities name, Sample: Huaxia Bank)
=====
Table: Balance_Sheet
Column:
(Stk_Code, Comment: Securities code, Foreign key: references Basic_Info(Stk_Code))
=====
Table: Income_Statement
Column:
(Stk_Code, Comment: Securities code, Foreign key: references Basic_Info(Stk_Code))
(Fee_com_inc, Comment: Fee and commission income)
(Fee_com_exp, Comment: Handling fees and commission expenses)
[Question]
What is the fee and commission income of Huaxia Bank?
[Answer]
{{
  "Basic_Info": ["Stk_Code","Stk_Name"],
  "Balance_Sheet": [],
  "Income_Statement": ["Stk_Code","Fee_com_inc"]
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


decomposer_template = """
You are an experienced financial database administrator.
You need to follow the instructions below to solve the problem step by step:
1. Decompose the question into sub questions
2. Use the {} dialect to generate SQL statements in the same format as the [Answer] part of the example

Requirements:
When you have generated a SQL statement that already solves the problem, there is no need to generate more text

Example:
[Schema]
=====
Table: Basic_Info
Column:
(Stk_Code, Comment: Securities code, Primary key)
(Stk_Name, Comment: Securities name)
=====
Table: Balance_Sheet
Column:
(Stk_Code, Comment: Securities code, Foreign key: references Basic_Info(Stk_Code))
(Cash_CB, Comment: Cash and deposits with central bank)
[Question]
List securities codes and securities names with cash and deposits with central bank over the average.
[Answer]
Sub question 1: Get the average value of cash and deposits with central bank.
```sql
SELECT AVG(Cash_CB) FROM Balance_Sheet
```
Sub question 2: List securities codes and securities names with cash and deposits with central bank over the average.
```sql
SELECT b1.Stk_Code, b1.Stk_Name 
FROM Balance_Sheet AS b1 INNER JOIN Basic_Info AS b2 
ON b1.Stk_Code = b2.Stk_Code
WHERE Cash_CB > (SELECT AVG(Cash_CB) FROM Balance_Sheet)
```
This SQL statement already solves the problem, so there is no need to continue generating text.

Please start solving the problem:
[Schema]
{}
[Question]
{}
"""

decomposer_hint_template = """[Hint]
You can refer to following information:
{}
"""

reviser_template = """
[Task]
You are an experienced financial database administrator.
When executing SQL below, some errors occurred, please fix up SQL and generate new SQL based on the information given.
Solve the task step by step if you need. When you find an answer, verify the answer carefully. 

[SQL Constraints]
When generating SQL, we should always consider constraints:
- In `SELECT <column>`, just select needed columns in the [Question] without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

[Schema]
{}
[Hint]
{}
[Question]
{}
[old SQL]
```sql
{}
```
[SQLite error]
{}

Now please fix up old SQL and generate new SQL again.
The format of the new SQL is as follows.
```sql

```
[correct SQL]
"""
