from pydantic import BaseModel, constr


class PostBase(BaseModel):
    text: constr(max_length=1024)


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
