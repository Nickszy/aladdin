from sqlmodel import Session, select
from typing import List, Optional
from aladdin.models.feed import Feed

class FeedService:
    def __init__(self, session: Session):
        self.session = session
    
    def get_feed_by_id(self, feed_id: str) -> Optional[Feed]:
        """根据ID查询feed"""
        return self.session.get(Feed, feed_id)
    
    def get_all_feeds(self, offset: int = 0, limit: int = 100) -> List[Feed]:
        """查询所有feeds（支持分页）"""
        statement = select(Feed).offset(offset).limit(limit)
        return list(self.session.exec(statement))
    
    def get_feeds_by_owner(self, owner_user_id: str) -> List[Feed]:
        """根据ownerUserId查询feeds"""
        statement = select(Feed).where(Feed.ownerUserId == owner_user_id)
        return list(self.session.exec(statement))
    
    def get_feeds_with_errors(self) -> List[Feed]:
        """查询有错误的feeds"""
        statement = select(Feed).where(Feed.errorMessage.isnot(None))
        return list(self.session.exec(statement))
    
    def create_feed(self, feed: Feed) -> Feed:
        """创建新的feed"""
        self.session.add(feed)
        self.session.commit()
        self.session.refresh(feed)
        return feed
    
    def update_feed(self, feed: Feed) -> Feed:
        """更新feed"""
        self.session.add(feed)
        self.session.commit()
        self.session.refresh(feed)
        return feed
    
    def delete_feed(self, feed_id: str) -> bool:
        """删除feed"""
        feed = self.session.get(Feed, feed_id)
        if feed:
            self.session.delete(feed)
            self.session.commit()
            return True
        return False