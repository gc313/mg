
import Module.database as db
import Module.config as con
import Module.handler as hd
def aaa(**kw):
    tail = " ".join(key+" "+value for key, value in kw.items())
    for key, value in kw.items():
        print(key, value)

    print(kw)
    print(tail)

def bbb(**kw):
    tail = ",".join(key for key in kw.keys())
    tail2 = ",".join(value for value in kw.values())
    for i in kw:
        print(i)


    print(kw)
    print(tail)
    print(tail2)

#aaa(where = "id = %s" % '0123', oredr_by = "name", limit = "10 offset 3")

#a = db.TorF(con.uni_db, "H_sec_location", 60012157)
#print(a)
b = hd.check_security(30000571)
print(b)
