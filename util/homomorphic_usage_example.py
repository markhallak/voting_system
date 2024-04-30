# from bfv.batch_encoder import BatchEncoder
# from bfv.bfv_decryptor import BFVDecryptor
# from bfv.bfv_encryptor import BFVEncryptor
# from bfv.bfv_evaluator import BFVEvaluator
# from bfv.bfv_key_generator import BFVKeyGenerator
# from bfv.bfv_parameters import BFVParameters
#
#
#
# message1 = [0, 2]
# message2 = [0, 1]
#
# plain1 = encoder.encode(message1)
# plain2 = encoder.encode(message2)
# ciph1 = encryptor.encrypt(plain1)
# ciph2 = encryptor.encrypt(plain2)
# ciph_prod = evaluator.add(ciph1, ciph2)
# decrypted_prod = decryptor.decrypt(ciph_prod)
# decoded_prod = encoder.decode(decrypted_prod)
#
# print(decoded_prod)
