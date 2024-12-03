from typing import Annotated, Literal
from typing import cast

from flask import Blueprint, session, request
from flask_login import login_required, login_user, current_user
from flask_pydantic import validate

from webauthn import generate_registration_options, verify_registration_response
from webauthn import generate_authentication_options, verify_authentication_response
from webauthn import options_to_json, base64url_to_bytes

from pydantic import BaseModel, Field

from cyanoconstruct.database import db
from cyanoconstruct.database import WebAuthn, UserDataDB
from cyanoconstruct.users import UserData


_RP_ID = "localhost"
_ORIGIN = "http://localhost:3000"


auth = Blueprint("auth", __name__, template_folder="templates")


class RegisterStartRequestExisting(BaseModel):
    initial: Literal[False]


class RegisterStartRequestInitial(BaseModel):
    initial: Literal[True]
    email: str


RegisterStartRequest = Annotated[
    RegisterStartRequestExisting | RegisterStartRequestInitial,
    Field(discriminator="initial"),
]

# @app.route("/registerProcess", methods=["POST"])
def registerProcess():
    """Register a user using an email.

    NOTE:
            This function should not be called upon in the final site.
    """
    validInput = False
    outputStr = ""
    succeeded = False

    # get information from the page's form
    try:
        email = request.form["email"]
        try:
            remember = rf.boolJS(request.form["remember"])
        except Exception:
            raise ValueError("invalid remember me")

        validInput = True

    except Exception:
        outputStr = "ERROR: could not get valid data from form.<br>"

    # try to register a new account
    if validInput:
        try:
            user = UserData.new(email)
            login_user(user, remember=remember)

            clearSelected()

            # indicate success
            outputStr += "Successfully registered and logged in as {email}.<br>".format(
                email=email
            )
            succeeded = True
        except Exception as e:
            outputStr += "ERROR: " + str(e) + "<br>"

    return jsonify({"output": outputStr, "succeeded": succeeded})


@auth.route("/auth/register/start", methods=["POST"])
@validate()
def webauthn_register_start(body: RegisterStartRequest):
    match body, current_user.is_authenticated:
        case RegisterStartRequestInitial(), False:
            email = body.email
        case RegisterStartRequestExisting(), True:
            email = current_user.getEmail()
            pass
        case _:
            return {"error": "invalid request"}, 400
    
    # TODO(tnytown): why can't simplewebauthn handle our full-length user_id ? , user_id=token_hex(64).encode()
    opts = generate_registration_options(rp_id=_RP_ID, rp_name="cyanoConstruct", user_name=email)
    session["webauthn_register"] = (opts.user.name, opts.challenge)

    return options_to_json(opts), 200, {"Content-Type": "application/json"}


@auth.route("/auth/register/verify", methods=["POST"])
def webauthn_register_verify():
    (email, challenge) = session.pop("webauthn_register")
    if not challenge:
        return {"error": "no active WebAuthN challenge"}, 400
    
    credential = request.json

    result = verify_registration_response(
        credential=credential,
        expected_challenge=challenge,
        expected_rp_id=_RP_ID,
        expected_origin=_ORIGIN
    )

    user: UserDataDB = db.session.execute(db.select(UserDataDB).where(UserDataDB.email == email)).one().UserDataDB

    webauthn = WebAuthn(id=result.credential_id, public_key=result.credential_public_key)
    user.webauthn.append(webauthn)
    db.session.commit()

    return {"verified": True}, 200


@auth.route("/auth/methods", methods=["GET"])
@login_required
def webauthn_get_methods():
    user = cast(UserData, current_user).getEntry()
    return user.webauthn, 200


@auth.route("/auth/login/start")
def webauthn_login_start():
    opts = generate_authentication_options(rp_id=_RP_ID)
    session["webauthn_login"] = opts.challenge

    return options_to_json(opts), 200, {"Content-Type": "application/json"}

@auth.route("/auth/login/verify", methods=["POST"])
def webauthn_login_verify():
    challenge = session.pop("webauthn_login")
    if not challenge:
        return {"error": "No active WebAuthn challenge"}, 400
    
    payload = request.json
    credential_id = base64url_to_bytes(payload["id"])

    webauthn: WebAuthn | None = db.session.scalar(db.select(WebAuthn).where(WebAuthn.id == credential_id))
    if webauthn is None:
        return "{}", 401
    
    result = verify_authentication_response(
        credential=payload,
        expected_challenge=challenge,
        expected_rp_id=_RP_ID,
        expected_origin=_ORIGIN,
        credential_public_key=webauthn.public_key,
        credential_current_sign_count=webauthn.counter
    )
    webauthn.counter = result.new_sign_count
    db.session.commit()
    
    print(result)

    # TODO(tnytown): plumb through remember
    login_user(UserData.from_db(webauthn.user), remember=False)
    
    return {"verified": True}, 200
