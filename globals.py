from django.conf import settings
from supabase import create_client

from util.bfv.batch_encoder import BatchEncoder
from util.bfv.bfv_decryptor import BFVDecryptor
from util.bfv.bfv_encryptor import BFVEncryptor
from util.bfv.bfv_evaluator import BFVEvaluator
from util.bfv.bfv_key_generator import BFVKeyGenerator
from util.bfv.bfv_parameters import BFVParameters

# Supabase
sp = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Homomorphic
degree = 2
plain_modulus = 17
ciph_modulus = 8000000000000
params = BFVParameters(poly_degree=degree,
                       plain_modulus=plain_modulus,
                       ciph_modulus=ciph_modulus)
key_generator = BFVKeyGenerator(params)
homomorphicPublicKey = key_generator.public_key
homomorphicPrivateKey = key_generator.secret_key
relin_key = key_generator.relin_key
encoder = BatchEncoder(params)
encryptor = BFVEncryptor(params, homomorphicPublicKey)
decryptor = BFVDecryptor(params, homomorphicPrivateKey)
evaluator = BFVEvaluator(params)


