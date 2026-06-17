from pydantic import BaseModel, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str = "Bearer"


# ── STK Push ──────────────────────────────────────────────────────────────────

class STKPushRequest(BaseModel):
    phone_number: str
    amount: int
    account_reference: str
    transaction_desc: str
    callback_url: str


class STKPushResponse(BaseModel):
    merchant_request_id: str = Field(alias="MerchantRequestID")
    checkout_request_id: str = Field(alias="CheckoutRequestID")
    response_code: str = Field(alias="ResponseCode")
    response_description: str = Field(alias="ResponseDescription")
    customer_message: str = Field(alias="CustomerMessage")

    model_config = {"populate_by_name": True}


class STKQueryResponse(BaseModel):
    response_code: str = Field(alias="ResponseCode")
    response_description: str = Field(alias="ResponseDescription")
    merchant_request_id: str = Field(alias="MerchantRequestID")
    checkout_request_id: str = Field(alias="CheckoutRequestID")
    result_code: str = Field(alias="ResultCode")
    result_desc: str = Field(alias="ResultDesc")

    model_config = {"populate_by_name": True}


# ── C2B ───────────────────────────────────────────────────────────────────────

class C2BRegisterRequest(BaseModel):
    confirmation_url: str
    validation_url: str
    shortcode: str | None = None
    response_type: str = "Completed"  # "Completed" | "Cancelled"


class C2BRegisterResponse(BaseModel):
    conversation_id: str = Field(alias="ConversationID")
    originator_conversation_id: str = Field(alias="OriginatorConverstionID")
    response_description: str = Field(alias="ResponseDescription")

    model_config = {"populate_by_name": True}


# ── B2C ───────────────────────────────────────────────────────────────────────

class B2CResponse(BaseModel):
    conversation_id: str = Field(alias="ConversationID")
    originator_conversation_id: str = Field(alias="OriginatorConversationID")
    response_code: str = Field(alias="ResponseCode")
    response_description: str = Field(alias="ResponseDescription")

    model_config = {"populate_by_name": True}
