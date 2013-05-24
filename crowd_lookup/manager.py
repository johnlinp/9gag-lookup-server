import models
#import tools

class Manager:
    pass

class WordMgr(Manager):
    def get(self, **kwargs):
        if 'word_str' in kwargs:
            return self._get_by_str(kwargs['word_str'])
        elif 'word_id' in kwargs:
            return self._get_by_id(kwargs['word_id'])
        assert False

    def _get_by_str(self, word_str):
        #word_str = tools.normalize_str(word_str)
        if word_str == '':
            return None
        words = models.Word.objects.filter(content=word_str)
        if not words:
            word = models.Word(content=word_str)
            word.save()
        else:
            assert len(words) == 1
            word = words[0]
        return word

    def _get_by_id(self, word_id):
        try:
            return models.Word.objects.get(id=word_id)
        except:
            return None

class RecommMgr(Manager):
    def get(self, gag_id, word):
        recomms = models.Recomm.objects.filter(gag_id=gag_id, word=word)
        if not recomms:
            return None
        assert len(recomms) == 1
        recomm = recomms[0]
        return recomm

    def query(self, gag_id, **kwargs):
        if 'user' not in kwargs:
            return self._query_by_gag_id(gag_id)
        else:
            if 'valence' not in kwargs:
                return None
            return self._query_by_user(gag_id, kwargs['user'], kwargs['valence'])
        return None

    def _query_by_gag_id(self, gag_id):
        recomms = models.Recomm.objects.filter(gag_id=gag_id, score__gt=0.5)
        return recomms

    def _query_by_user(self, gag_id, user, valence):
        records = models.RecommRecord.objects.filter(user=user, val_type=valence)
        recomms = [record.recomm for record in records if record.recomm.gag_id == gag_id]
        return recomms

    def going_up(self, word, gag_id, user):
        recomm = self.get(gag_id, word)
        record = self._get_record(user, recomm)
        if self._went_to(record, models.RecommRecord.VAL_POSITIVE):
            return
        if not recomm:
            recomm = self._create(gag_id, word)
        self._change_score(recomm, +1.0)
        self._leave_record(record, recomm, user, models.RecommRecord.VAL_POSITIVE)

    def going_down(self, word, gag_id, user):
        recomm = self.get(gag_id, word)
        record = self._get_record(user, recomm)
        if self._went_to(record, models.RecommRecord.VAL_NEGATIVE):
            return False
        if not recomm:
            return False
        self._change_score(recomm, -1.0)
        self._leave_record(record, recomm, user, models.RecommRecord.VAL_NEGATIVE)
        return True

    def _get_record(self, user, recomm):
        records = models.RecommRecord.objects.filter(user=user, recomm=recomm)
        if not records:
            return None
        assert len(records) == 1
        record = records[0]
        return record

    def _went_to(self, record, valence):
        if record == None:
            return False
        return record.val_type == valence

    def _create(self, gag_id, word):
        recomm = models.Recomm(gag_id=gag_id, word=word, score=0.0)
        recomm.save()
        return recomm

    def _change_score(self, recomm, score_delta):
        assert recomm
        recomm.score += score_delta
        recomm.save()
        
    def _leave_record(self, record, recomm, user, valence):
        if record:
            record.val_type = valence
        else:
            assert recomm
            record = models.RecommRecord(user=user, recomm=recomm, val_type=valence)
        record.save()

class ExplainMgr(Manager):
    def get(self, **kwargs):
        if 'expl_str' in kwargs and 'word' in kwargs:
            return self._get_by_str(kwargs['expl_str'], kwargs['word'])
        elif 'expl_id' in kwargs:
            return self._get_by_id(kwargs['expl_id'])
        assert False

    def _get_by_str(self, expl_str, word):
        #expl_str = tools.normalize_str(expl_str)
        if expl_str == '':
            return None
        expls = models.Explain.objects.filter(content=expl_str, word=word)
        if not expls:
            expl = models.Explain(word=word,
                                  repr_type=self._guess_repr_type(expl_str),
                                  content=expl_str,
                                  source='User Provide',
                                  link='')
            expl.save()
        else:
            assert len(expls) == 1
            expl = expls[0]
        return expl

    def _get_by_id(self, expl_id):
        try:
            return models.Explain.objects.get(id=expl_id)
        except:
            return None

    def _guess_repr_type(self, expl_str):
        # TODO: guess the representation type of the user given explain
        return models.Explain.REPR_TEXT

    def query(self, word, gag_id, user):
        expls = models.Explain.objects.filter(word=word)
        return expls

class UserMgr(Manager):
    def get(self, user_id):
        try:
            return models.User.objects.get(id=user_id)
        except:
            return None

class AllManagers:
    def __init__(self):
        self.word = WordMgr()
        self.recomm = RecommMgr()
        self.explain = ExplainMgr()
        self.user = UserMgr()

