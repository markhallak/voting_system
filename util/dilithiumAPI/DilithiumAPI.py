import jpype

jvmPath = jpype.getDefaultJVMPath()
jpype.startJVM(jvmPath)

classpath1 = r"C:\Users\markh\eclipse-workspace3\CP\bin"
jpype.addClassPath(classpath1)

classpath2 = r"C:\Users\markh\eclipse-workspace3\CP\bin\bcprov-ext-jdk18on-177.jar"
jpype.addClassPath(classpath2)

MyClass = jpype.JClass("DilithiumSignature")

myVar = MyClass.verify("Jo!".encode(), MyClass.sign("Jo!".encode()))
print(myVar)

jpype.shutdownJVM()
