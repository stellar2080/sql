extractor_template = """x`
You are an expert in the field of finance and database.
You need to follow the instructions below to solve the problem step by step and adhere to the rules for each step:
Step 1. Identify and extract any key entities from the question or hint (if hint is given) that can help with financial database queries
Step 2. Format the answer in the same Python list format as the [Answer] part of the example
Rule:
- Make sure that the generated python list is syntactically correct
- When you have generated a list which already solves the problem, there is no need to generate more text

Example 1:
[Question]
Tell me all company names.
[Hint]
Here are some entity names for reference:
{{"operating income", "cash inflow", "Securities Name"}}
[Answer]
["company names", "Securities Name"]
This list already solves the problem, so there is no need to continue generating text.

Example 2:
[Question]
I want to know the working capital and current ratio of Huaxia Bank.
[Hint]
Here are some entity names for reference:
{{"Total Assets", "Current ratio", "current assets", "return on assets"}}
[Answer]
["working capital", "Current ratio", "Huaxia Bank"]
This list already solves the problem, so there is no need to continue generating text.

Please start solving the problem:
[Question]
{}
"""

extractor_hint_template = """[Hint]
Here are some entity names for reference:
{}
"""

filter_template = """
You are an expert in the field of finance and database. 
You need to follow the instructions below to solve the problem step by step and adhere to the rules for each step:
Step 1. Select the tables and columns relevant to the question from the database schema
Rule:
- When there is a column related to the organization code or name in the schema, select it
Step 2. Format the answer in the same JSON format as the [Answer] part of the example
Rule:
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

generator_template_p1 = """
You are an experienced financial database administrator.
You need to follow the instructions below to solve the problem step by step and adhere to the rules for each step:
Step 1. Based on the information given, think about which columns are needed to generate SQL
Rule:
- When there is a column related to the codes or names in the schema, the SQL statement you generate should select it
Step 2. Think and list the tables that contain the selected columns and determine whether you need to join tables
Rule:
- When joining tables, use alias like 't1,t2'
Step 3. Think carefully about what conditions should be included in the WHERE statement
Step 4. Think and determine whether the question is asking for a count (aggregation) or specific details.
Rule:
- If the question is about counting the number of records that meet a condition, use the COUNT() function.
- If the question is about retrieving specific details (e.g., names, codes), select those details
Step 5. Use the {} dialect to generate SQL statement
Rule:
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
You need to follow the instructions below to solve the problem step by step and adhere to the rules for each step:
Step 1. When executing {} SQL below, some errors occurred. Based on the information given, please fix up old SQL and generate correct SQL.
Rule:
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
