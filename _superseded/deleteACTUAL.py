import pandas as pd
from sqlalchemy import create_engine

username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "03C_INFRASTRUCTURE_DEVELOPMENT"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database
)
devengine = create_engine(devconnection_uri)


oldinfdata = pd.read_sql("Select * FROM STANDARD_TAG_DATA", con=devengine)
oldinfdata["Key"] = (
    oldinfdata["Asset_Type"]
    + "_"
    + oldinfdata["Object_Group"]
    + oldinfdata["Tag_Attribute"]
)


oldinfdata.to_csv("old_Inf.csv", index=False)
