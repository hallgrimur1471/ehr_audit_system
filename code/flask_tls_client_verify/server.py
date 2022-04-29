# //TODO: for readme: how to create ca & client-certs:
# // ---> https://jamielinux.com/docs/openssl-certificate-authority/sign-server-and-client-certificates.html
# source: https://www.ajg.id.au/2018/01/01/mutual-tls-with-python-flask-and-werkzeug/
from flask import Flask, render_template, request
import werkzeug.serving
import ssl
from ssl import TLSVersion
import OpenSSL


class PeerCertWSGIRequestHandler(werkzeug.serving.WSGIRequestHandler):
    """
    We subclass this class so that we can gain access to the connection
    property. self.connection is the underlying client socket. When a TLS
    connection is established, the underlying socket is an instance of
    SSLSocket, which in turn exposes the getpeercert() method.
    The output from that method is what we want to make available elsewhere
    in the application.
    """

    def make_environ(self):
        """
        The superclass method develops the environ hash that eventually
        forms part of the Flask request object.
        We allow the superclass method to run first, then we insert the
        peer certificate into the hash. That exposes it to us later in
        the request variable that Flask provides
        """
        environ = super(PeerCertWSGIRequestHandler, self).make_environ()
        x509_binary = self.connection.getpeercert(True)
        x509 = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_ASN1, x509_binary
        )
        environ["peercert"] = x509
        return environ


app = Flask(__name__)
# to establish an SSL socket we need the private key and certificate that
# we want to serve to users.
#
# app_key_password here is None, because the key isn't password protected,
# but if yours is protected here's where you place it.
app_key = "./server.key"
app_key_password = None
app_cert = "./server.crt"
# in order to verify client certificates we need the certificate of the
# CA that issued the client's certificate. In this example I have a
# single certificate, but this could also be a bundle file.
# ca_cert = "./ca.crt"
ca_cert = "./FlexCA.pem"
# create_default_context establishes a new SSLContext object that
# aligns with the purpose we provide as an argument. Here we provide
# Purpose.CLIENT_AUTH, so the SSLContext is set up to handle validation
# of client certificates.
ssl_context = ssl.create_default_context(
    purpose=ssl.Purpose.CLIENT_AUTH, cafile=ca_cert
)
print(ssl_context.options)
# ssl_context.minimum_version = TLSVersion.TLSv1_3
print(ssl_context.minimum_version)
# load in the certificate and private key for our server to provide to clients.
# force the client to provide a certificate.
ssl_context.load_cert_chain(
    certfile=app_cert, keyfile=app_key, password=app_key_password
)
# ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
ssl_context.verify_mode = ssl.CERT_REQUIRED
# now we get into the regular Flask details, except we're passing in the peer certificate
# as a variable to the template.
import inspect


@app.route("/")
def hello_world():
    # ttps://www.pyopenssl.org/en/stable/api/crypto.html#x509-objects
    print(request.environ["peercert"].get_subject().commonName)
    return (
        "Congratulations on passing the TLS! "
        + str(request.environ["peercert"])
        + "\n"
    )
    # return render_template(
    #    "helloworld.html", client_cert=request.environ["peercert"]
    # )


# start our webserver!
if __name__ == "__main__":
    app.run(ssl_context=ssl_context, request_handler=PeerCertWSGIRequestHandler)
