from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import schemas, database, models, models, oauth2

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user : int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
  
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, details=f"Post with id {vote.post_id} not found")
  
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    if (vote.dir == 1 ):

        if found_vote:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="already voted")
        
        new_vote = models.Vote(post_id=vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)

        return new_vote

    else:

        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details=f"There is no vote found for user with id{vote.user_id} for a post with id{vote.post_id}")
        
        vote_query.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)