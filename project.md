I want to build a Pathlogy Laboratory management system agent using Langraph.

I will tell you what is to be done,as following
first can ask to llm for test which can be taken in lab,home,hospital or can ask for his report
ask for recipt of payment, if user ask anythink different than this then llm should not answer.
then llm goes to test confirmation node which decides wheter this test can be done in our lab do we
have required supplies etc ,so test can be done or not or partial test can be done x out of y this should have 
at max 3 tries and for asking llm 2 tries 
if test gets confirm user should get to know test can be done than this test goes to Lab test where it gives 
some output , this output should get varified by Pathology Doctor in charge lets say John if he varifies it then only
the report goes to llm and to the user ,else John will try to redo the test and send back to Lab Test
Lab test has atmax 2 tries if it fails then user should get notified that we are sorry we cant do test and should get refund

If user ask for report delivery after labtest and after getting varified llm should tell user that your report is on the ways
this also has atmax 2 tries if report delivery failes then again it should go back to llm get the report and update the user

In meanwhile if user has came by reference by doctor than that docter should also get involved after getting report docter should also get the report and doctor can for more test for that particular patient.