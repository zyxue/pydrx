import sqlalchemy
import time

from sqlalchemy import orm

from db_tables import YoungNode

engine = sqlalchemy.create_engine('sqlite:///{0}'.format("lala.db"), echo=True)
S = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False)

YoungNode.metadata.create_all(engine)

session = S()
# y = YoungNode("hostname0", time.time(), "000.000.000.000")
# session.add(y)

# session.add_all([
#         YoungNode("hostname1", time.time(), "111.111.111.111"),
#         YoungNode("hostname2", time.time(), "222.222.222.222"),
#         YoungNode("hostname3", time.time(), "333.333.333.333"),
#         YoungNode("hostname4", time.time(), "444.444.444.444"),
#         YoungNode("hostname5", time.time(), "555.555.555.555"),
#         YoungNode("hostname6", time.time(), "666.666.666.666"),
#         YoungNode("hostname7", time.time(), "777.777.777.777"),
#         YoungNode("hostname8", time.time(), "888.888.888.888"),
#         YoungNode("hostname9", time.time(), "999.999.999.999"),
#         ])

# session.all()
session.commit()
