import jpype


class DilithiumAPI:
    MyClass = None

    def __init__(self):
        jvmPath = jpype.getDefaultJVMPath()

        try:
            jpype.startJVM(jvmPath)
        except Exception as e:
            print("ERROR: " + str(e))

        classpath1 = r"C:\Users\markh\eclipse-workspace3\CP\bin"
        jpype.addClassPath(classpath1)

        classpath2 = r"C:\Users\markh\eclipse-workspace3\CP\bin\bcprov-ext-jdk18on-177.jar"
        jpype.addClassPath(classpath2)

        self.MyClass = jpype.JClass("DilithiumSignature")

    def getPairKey(self):
        instance = self.MyClass.getPairKey()
        return bytes(instance[0]).decode('ISO-8859-1'), bytes(instance[1]).decode("ISO-8859-1")

    def shutDown(self):
        jpype.shutdownJVM()

    def sign(self, content):
        return self.MyClass.sign(content)

    # myVar = MyClass.verify("Jo!".encode(), MyClass.sign("Jo!".encode()))
    # print(myVar)
