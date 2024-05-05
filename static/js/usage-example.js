import * as json from 'https://cdn.jsdelivr.net/npm/canonical-json-olpc@1.0.1/+esm';

import { Kyber1024 } from "https://cdn.jsdelivr.net/npm/crystals-kyber-js@1.1.1/+esm";


function generateDilithiumKeyPair(){
    const level = DilithiumAlgorithm.DilithiumLevel.get(5);
    const keyPair = DilithiumAlgorithm.DilithiumKeyPair.generate(level);
    return keyPair;
}

function sign(){
const message = new TextEncoder().encode("Joy!");
const signature = privateKey.sign(message);
return signature;
}

function verify(){
    return publicKey.verifySignature(new TextEncoder().encode("Joy!"), sign());
}

function stringify(obj){
    return json.canonicalize(obj);
}

async function doSomething() {
        var kyberPublicKey = document.querySelector('meta[name="kyberPublicKey"]').getAttribute('content');

        try {
          const sender = new Kyber1024();
          const [encapsulatedSharedSecret, plainSharedSecret] = await sender.encap(kyberPublicKey);


          console.log(encryptedData);



          return;
        } catch (err) {
          alert("failed: ", err.message);
        }
      }

//const keyPair = generateDilithiumKeyPair();
//const privateKey = keyPair.getPrivateKey();
//const publicKey = keyPair.getPublicKey();
//console.log("Valid: " + verify());

