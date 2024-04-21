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

    print(MyClass.getPublicKey())
    print(MyClass.getPrivateKey())

    # myVar = MyClass.verify("Jo!".encode(), MyClass.sign("Jo!".encode()))
    # print(myVar)

    jpype.shutdownJVM()
