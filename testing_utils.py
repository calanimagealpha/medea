import datetime
import random

from medea import logic
from medea.base import api_to_model_dict
from medea.db_operations import session_scope
from medea.models import Work, Creator, CreatorAlias, Tag, WorkPart, Role


def random_word_generator(words_to_return=1):
    word_source = "Shitai kara! Shitai nara! Shitai toki! Shitai desho!? Issho ni! (Hai!) Watashitachi wa koko ni imasu! Koko ni wa yume ga chanto aru Furendo nara tomodachi desho (Sou da!) Suki tte itte mita (Daisuki) Houkago nara atarimae no koto Saa sa atsumare kossori kaeru na (Koraa) Bukatsudou da ne katsudou shichau ne Asonderu nja arimasen!! Tadaima. tte ano ko ga iu yo (Okaeri) Minna de ireba daijoubu (Bu!) Everybody say! Tomodachi de iyo ne Shitai kara! Shitai nara! Shitai toki! Shitai desho!? Daisuki! (Hai!) Watashitachi wa tanoshinderu! N    ijuu-yon jikan hashaideru Okujou ni maaaka na taiyou Kanari sakende mita! (Genki desu!) Watashitachi wa koko ni imasu! Koko ni wa yume ga chanto aru Furendo nara tomodachi desho (Sou da!) Suki tte itte mita (Daisuki) Kiinkon! Kaankon! Kara no gekou taimu Iie watashita    chi mada kaeranai (Yada yo) Bukatsudou da yo katsuyaku shichau yo Shin nyuubu in boshuu chuu! Gomen ne. tte chiisaku iu yo (Ara maa~) Kenka suru hodo honyararara? (Honyara?) Never give up! Saikyou ni nareru ne Shitai kara! Shitai nara! Shitai toki! Shitai desho!? Issh    o ni! (Hai!) Watashitachi wa keiken suru! Tabete nemutte kashikoku naru Koutei ni suzukaze fuite Ookiku te wo furu (Mata ashita nee!) Watashitachi wa koko ni imasu! Koko ni wa yume ga chanto aru Furendo nara tomodachi desho (Sou da!) Suki tte itte mita (Daisuki) Minna     ga koko ni atsumareba Gakkou wa tokubetsu ni naru Kyou ga owatte mo ashita mo Egao de aeru ne! Watashitachi wa koko ni imasu! Koko ni wa yume ga chanto aru Furendo nara tomodachi desho Daisuki arigato!!"
    word_set = set(word_source.split(' '))
    random_words = random.sample(word_set, words_to_return)
    return ' '.join(random_words)

def create_fake_work(
    type=None,
    title=None,
    catalog_number=None,
    release_date=None,
    description=None,
    is_active=True,
):
    work_dict = {
        'type': type or random_word_generator(), # Change this if types become enums
        'title': title or random_word_generator(2),
        'catalog_number': catalog_number or 'CAT-{0}'.format(random.randint(10000,99999)),
        'release_date': release_date or datetime.datetime.today(),
        'description': description or random_word_generator(15),
        'is_active': is_active
    }
    with session_scope() as session:
        new_fake_work = Work(**work_dict)
        session.add(new_fake_work)
        session.commit()
        work_dict = api_to_model_dict({'work': new_fake_work.to_dict()})
        return work_dict

def create_fake_creator(
    name=None,
    is_group=False,
    alias_names=None
):
    creator_dict = {
        'name': name or random_word_generator(2),
        'is_group': is_group
    }
    alias_names = alias_names or []
    with session_scope() as session:
        new_fake_creator = Creator(**creator_dict)
        for alias_name in alias_names:
            new_alias = CreatorAlias(name=alias_name, creator=new_fake_creator)
        session.add(new_fake_creator)
        session.commit()
        creator_dict = api_to_model_dict({'creator': new_fake_creator.to_dict()})
        return creator_dict
