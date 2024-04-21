import jpype


class DilithiumAPI:
    MyClass = None

    def __init__(self):
        jvmPath = jpype.getDefaultJVMPath()
        jpype.startJVM(jvmPath)

        classpath1 = r"C:\Users\markh\eclipse-workspace3\CP\bin"
        jpype.addClassPath(classpath1)

        classpath2 = r"C:\Users\markh\eclipse-workspace3\CP\bin\bcprov-ext-jdk18on-177.jar"
        jpype.addClassPath(classpath2)

        self.MyClass = jpype.JClass("DilithiumSignature")

    def getPublicKey(self):
        return self.MyClass.getPublicKey()

    def getPrivateKey(self):
        return self.MyClass.getPrivateKey()

    def shutDown(self):
        jpype.shutdownJVM()

    def sign(self, content):
        return self.MyClass.sign(content)

    # myVar = MyClass.verify("Jo!".encode(), MyClass.sign("Jo!".encode()))
    # print(myVar)

