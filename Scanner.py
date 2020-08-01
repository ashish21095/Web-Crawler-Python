import time
from  Enveda import Enveda_parser



Scanner = Enveda_parser("http://alkamid.ugent.be/alkamidresults.php?from=0&amount=20&query=")

t0 = time.time()

Scanner.main_function()

t1 = time.time()
print(f"{t1-t0} seconds to execute")