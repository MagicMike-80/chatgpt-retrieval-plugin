"""Episode data for the Thai Folklore series (EP1-10).

Single source of truth for timing, characters and voice-over lines.
`voice_generator.py` reads this to produce ElevenLabs MP3s + a SyncFrame manifest.
The Google Flow visual prompts live in `master_prompts/EP*.md`.

Scene grid is identical across all episodes:
    S1 00:00-01:30  cold open
    S2 01:30-03:30  setup
    S3 03:30-05:30  first contact
    S4 05:30-07:30  escalation
    S5 07:30-09:30  confrontation
    S6 09:30-11:00  resolution + next-episode hook
"""

SCENE_GRID = [
    (1, "00:00", "01:30"),
    (2, "01:30", "03:30"),
    (3, "03:30", "05:30"),
    (4, "05:30", "07:30"),
    (5, "07:30", "09:30"),
    (6, "09:30", "11:00"),
]

# Map a speaker to an ElevenLabs voice id. Fill these in from your account —
# the generator will refuse to run on a placeholder rather than burn credits.
VOICES = {
    "Narrator TH": "REPLACE_WITH_VOICE_ID",
    "Narrator EN": "REPLACE_WITH_VOICE_ID",
    "Mae Nak": "REPLACE_WITH_VOICE_ID",
    "Mak": "REPLACE_WITH_VOICE_ID",
    "Village Elder": "REPLACE_WITH_VOICE_ID",
    "Thai Old Man": "REPLACE_WITH_VOICE_ID",
    "Lucy": "REPLACE_WITH_VOICE_ID",
    "Gummi-Face": "REPLACE_WITH_VOICE_ID",
    "Nuan": "REPLACE_WITH_VOICE_ID",
    "Somchai": "REPLACE_WITH_VOICE_ID",
    "Phra Sombat": "REPLACE_WITH_VOICE_ID",
    "Nang Tani": "REPLACE_WITH_VOICE_ID",
    "Mor Tham": "REPLACE_WITH_VOICE_ID",
    "Bua": "REPLACE_WITH_VOICE_ID",
    "Khun Anan": "REPLACE_WITH_VOICE_ID",
    "Kuman": "REPLACE_WITH_VOICE_ID",
    "Ploy": "REPLACE_WITH_VOICE_ID",
    "Ranger Wit": "REPLACE_WITH_VOICE_ID",
    "Foreman Krit": "REPLACE_WITH_VOICE_ID",
    "Nang Ta-khian": "REPLACE_WITH_VOICE_ID",
}


def _scene(n, title, characters, vo):
    start, end = SCENE_GRID[n - 1][1], SCENE_GRID[n - 1][2]
    return {
        "scene": n,
        "start": start,
        "end": end,
        "title": title,
        "characters": characters,
        "vo": vo,
    }


def _line(speaker, lang, text):
    return {"speaker": speaker, "lang": lang, "text": text}


EPISODES = [
    {
        "episode": 1,
        "title": "Mae Nak — The Wife Who Would Not Leave",
        "thai_title": "แม่นาคพระโขนง",
        "creature": "Mae Nak Phra Khanong",
        "logline": "A soldier comes home from war to a wife who died while he was gone "
                   "— and a village too frightened to tell him.",
        "scenes": [
            _scene(1, "The arm that reached too far", ["Mae Nak", "Narrator TH"], [
                _line("Narrator TH", "th", "ที่พระโขนง ไม่มีใครกล้าพูดชื่อเธอดัง ๆ"),
                _line("Narrator EN", "en", "In Phra Khanong, no one says her name out loud."),
                _line("Mae Nak", "th", "สามีฉัน... ยังไม่กลับมา"),
            ]),
            _scene(2, "Mak comes home", ["Mak", "Mae Nak"], [
                _line("Mak", "th", "นาค! ผมกลับมาแล้ว ผมกลับมาแล้วจริง ๆ"),
                _line("Mae Nak", "th", "พี่มาก ฉันรอมานานแล้ว ข้าวยังอุ่นอยู่เลย"),
                _line("Narrator EN", "en", "He had been gone two years. The rice was still warm."),
            ]),
            _scene(3, "The village will not look at him", ["Village Elder", "Mak"], [
                _line("Village Elder", "th", "ไอ้มาก... เมียเอ็งตายไปตั้งแต่ปีกลายแล้ว"),
                _line("Mak", "th", "ลุงพูดอะไรของลุง เมื่อคืนเธอยังหุงข้าวให้ผมกิน"),
                _line("Narrator EN", "en", "Every neighbour who tried to warn him was found silent by morning."),
            ]),
            _scene(4, "The lime under the house", ["Mak", "Mae Nak"], [
                _line("Narrator TH", "th", "มะนาวลูกนั้น กลิ้งลงไปใต้ถุนบ้าน"),
                _line("Narrator EN", "en", "The lime rolled off the porch. She did not walk down for it."),
                _line("Mak", "th", "แขน... แขนเธอ..."),
            ]),
            _scene(5, "Running to the temple", ["Mak", "Mae Nak"], [
                _line("Mae Nak", "th", "พี่มาก! อย่าทิ้งฉันนะ ฉันรอมาสองปี!"),
                _line("Mak", "th", "นาค ผมขอโทษ ผมขอโทษจริง ๆ"),
                _line("Narrator EN", "en", "Holy ground. She could follow him to the wall and no further."),
            ]),
            _scene(6, "The jar in the river", ["Village Elder", "Mae Nak"], [
                _line("Village Elder", "th", "เขาขังวิญญาณเธอไว้ในหม้อดิน แล้วปล่อยลงแม่น้ำ"),
                _line("Narrator EN", "en", "They sealed her in a clay jar and gave her to the river. "
                                           "People still leave dresses at her shrine. Someone is still asking her for things."),
                _line("Mae Nak", "th", "ฉันไม่เคยอยากทำร้ายใคร ฉันแค่อยากให้เขากลับบ้าน"),
            ]),
        ],
    },
    {
        "episode": 2,
        "title": "The Last Emotion",
        "thai_title": "อารมณ์สุดท้าย",
        "creature": "Gummi-Face (original)",
        "logline": "An old man in a Bangkok shophouse sells the feelings people no longer "
                   "want to carry — and something soft is collecting them.",
        "scenes": [
            _scene(1, "The shop with no sign", ["Thai Old Man", "Narrator EN"], [
                _line("Narrator EN", "en", "The shop has no sign. People find it on the worst night of their life."),
                _line("Thai Old Man", "th", "เข้ามาสิ ไม่ต้องถอดรองเท้าก็ได้ เดี๋ยวก็ไม่รู้สึกอะไรแล้ว"),
            ]),
            _scene(2, "What he takes in trade", ["Thai Old Man"], [
                _line("Thai Old Man", "th", "ฉันไม่รับเงิน ฉันรับความรู้สึก"),
                _line("Narrator EN", "en", "Grief. Shame. The specific dread of a phone ringing at 3 a.m. He takes it all."),
            ]),
            _scene(3, "The jars in the back room", ["Thai Old Man", "Gummi-Face"], [
                _line("Narrator EN", "en", "Behind the curtain: shelves of jars, and each jar is breathing."),
                _line("Gummi-Face", "en", "You gave it away. That means it is mine now."),
            ]),
            _scene(4, "It learns a face", ["Gummi-Face", "Thai Old Man"], [
                _line("Gummi-Face", "en", "I wore your mother's face because you handed me the feeling attached to it."),
                _line("Thai Old Man", "th", "อย่ามองมัน อย่าให้มันรู้ว่าเจ็บตรงไหน"),
            ]),
            _scene(5, "The old man's own jar", ["Thai Old Man", "Gummi-Face"], [
                _line("Thai Old Man", "th", "ฉันขายไปหมดแล้ว เหลือแค่ความกลัวอย่างเดียว"),
                _line("Gummi-Face", "en", "Then give me the last one, and you will finally be quiet."),
            ]),
            _scene(6, "The shop is open again", ["Gummi-Face", "Narrator EN"], [
                _line("Narrator EN", "en", "In the morning the shop is open. Someone is behind the counter. "
                                           "He is very kind, and his face does not quite sit still."),
                _line("Gummi-Face", "th", "เข้ามาสิ อยากทิ้งอะไรไว้กับฉันล่ะ"),
            ]),
        ],
    },
    {
        "episode": 3,
        "title": "The Mirror Drip",
        "thai_title": "หยดในกระจก",
        "creature": "Gummi-Face (original)",
        "logline": "An English girl in a Bangkok apartment notices her bathroom mirror is "
                   "wet on the inside.",
        "scenes": [
            _scene(1, "One drop, wrong side", ["Lucy", "Narrator EN"], [
                _line("Narrator EN", "en", "The condensation ran down the inside of the glass. Not the room. The glass."),
                _line("Lucy", "en", "That's — no. That's not how mirrors work."),
            ]),
            _scene(2, "Nobody else can see it", ["Lucy", "Thai Old Man"], [
                _line("Lucy", "en", "It's warm. The mirror is warm and the flat is freezing."),
                _line("Thai Old Man", "th", "หนู อย่าเช็ดมันนะ ยิ่งเช็ดมันยิ่งรู้ว่าหนูอยู่ตรงไหน"),
            ]),
            _scene(3, "Her reflection is late", ["Lucy", "Gummi-Face"], [
                _line("Lucy", "en", "I raised my hand and it waited. Half a second. It waited."),
                _line("Gummi-Face", "en", "I am learning the timing. I will be perfect by Thursday."),
            ]),
            _scene(4, "Every reflective surface", ["Lucy"], [
                _line("Lucy", "en", "Kettle. Phone screen. The oven door. It's in all of them now."),
                _line("Narrator EN", "en", "She taped over the mirror. The tape sagged, from the inside, in the shape of a palm."),
            ]),
            _scene(5, "The swap", ["Lucy", "Gummi-Face"], [
                _line("Gummi-Face", "en", "Come closer. You have never once looked at yourself this kindly."),
                _line("Lucy", "en", "Whatever you are — you don't get to be me."),
            ]),
            _scene(6, "Which side she woke up on", ["Lucy", "Gummi-Face"], [
                _line("Narrator EN", "en", "She woke up in her own bed. The room was fine. The window was on the wrong wall."),
                _line("Gummi-Face", "th", "ยินดีต้อนรับ อยู่ในนี้เงียบดีนะ"),
            ]),
        ],
    },
    {
        "episode": 4,
        "title": "Krasue — The Hunger Below the Head",
        "thai_title": "กระสือ",
        "creature": "Krasue",
        "logline": "A village midwife keeps delivering healthy babies. The village keeps "
                   "losing chickens, then livestock, then more.",
        "scenes": [
            _scene(1, "A light over the rice field", ["Narrator TH", "Nuan"], [
                _line("Narrator TH", "th", "กลางดึก มีแสงสีแดงลอยอยู่เหนือทุ่งนา"),
                _line("Narrator EN", "en", "A red light drifting over the paddy. Too low for a star. Too slow for a bird."),
            ]),
            _scene(2, "Nuan, who is kind to everyone", ["Nuan", "Somchai"], [
                _line("Somchai", "th", "พี่นวลใจดีที่สุดในหมู่บ้านแล้ว ใครป่วยก็ไปหาพี่เขา"),
                _line("Nuan", "th", "กลางคืนอย่าออกจากบ้านนะ ยุงมันชุม"),
            ]),
            _scene(3, "The body without a head", ["Somchai"], [
                _line("Somchai", "th", "ตัวเธอ... นั่งอยู่ตรงนั้น แต่หัวไม่อยู่"),
                _line("Narrator EN", "en", "The body sits upright and waits. Wherever the head is, it has to come back before dawn."),
            ]),
            _scene(4, "What the light eats", ["Nuan", "Narrator TH"], [
                _line("Narrator TH", "th", "ไก่หาย หมูหาย แล้วก็ถึงคราวคนท้อง"),
                _line("Nuan", "th", "ฉันกลั้นมันไม่ไหวแล้ว มันหิวไม่ใช่ฉันหิว"),
            ]),
            _scene(5, "Thorns around the house", ["Somchai", "Nuan"], [
                _line("Somchai", "th", "เอาหนามไผ่ล้อมใต้ถุนไว้ ถ้ามันลงมาไม่ได้ มันก็กลับตัวไม่ได้"),
                _line("Nuan", "th", "ขอร้อง ปล่อยฉันกลับเข้าตัวเถอะ ใกล้สว่างแล้ว"),
            ]),
            _scene(6, "Sunrise", ["Somchai", "Narrator EN"], [
                _line("Narrator EN", "en", "At sunrise they found a body with no head, and a head with nowhere to go."),
                _line("Somchai", "th", "เขาว่ากันว่า ถ้าคนเป็นกระสือใกล้ตาย มันจะหาคนรับต่อ"),
            ]),
        ],
    },
    {
        "episode": 5,
        "title": "Nang Tani — The Woman in the Banana Grove",
        "thai_title": "นางตานี",
        "creature": "Nang Tani",
        "logline": "A young monk is told never to cut the banana tree behind the temple. "
                   "A developer is not told anything at all.",
        "scenes": [
            _scene(1, "Green under a full moon", ["Nang Tani", "Narrator TH"], [
                _line("Narrator TH", "th", "คืนเพ็ญ ใต้ต้นกล้วยตานี ผู้หญิงห่มเขียวยืนอยู่"),
                _line("Narrator EN", "en", "Full moon. Under the tani banana tree, a woman in green, feet not quite touching."),
            ]),
            _scene(2, "The rule at the temple", ["Phra Sombat"], [
                _line("Phra Sombat", "th", "ต้นนั้นห้ามตัด ผูกผ้าไว้แล้ว มีเจ้าของ"),
                _line("Narrator EN", "en", "The cloth around the trunk is not decoration. It is an address."),
            ]),
            _scene(3, "She feeds the hungry", ["Nang Tani", "Phra Sombat"], [
                _line("Nang Tani", "th", "หิวไหม กินเถอะ ฉันไม่ได้ทำร้ายคนที่ไม่ทำร้ายฉัน"),
                _line("Phra Sombat", "th", "รับได้ แต่อย่ารับปากอะไรทั้งนั้น"),
            ]),
            _scene(4, "The chainsaw", ["Narrator EN", "Nang Tani"], [
                _line("Narrator EN", "en", "The survey crew came at noon, when nobody believes in anything."),
                _line("Nang Tani", "th", "ฉันอยู่ตรงนี้มาก่อนวัด ก่อนถนน ก่อนพวกแก"),
            ]),
            _scene(5, "Sap like blood", ["Phra Sombat", "Nang Tani"], [
                _line("Phra Sombat", "th", "ยางมันสีแดง... หยุดเดี๋ยวนี้!"),
                _line("Nang Tani", "th", "สายไปแล้ว แกตัดบ้านฉันไปแล้วครึ่งหลัง"),
            ]),
            _scene(6, "A new grove", ["Phra Sombat", "Narrator EN"], [
                _line("Phra Sombat", "th", "ปลูกใหม่ ผูกผ้าใหม่ แล้วขอขมาให้ถูกวิธี"),
                _line("Narrator EN", "en", "Look at the banana trees behind any old Thai temple. Count the ones wearing cloth."),
            ]),
        ],
    },
    {
        "episode": 6,
        "title": "Phi Pop — The Thing That Wears You",
        "thai_title": "ผีปอบ",
        "creature": "Phi Pop",
        "logline": "In an Isan village, people start dying from the inside. The spirit does "
                   "not haunt a house. It haunts a person — and it moves.",
        "scenes": [
            _scene(1, "A woman eating in the dark", ["Narrator TH"], [
                _line("Narrator TH", "th", "ตีสาม มีเสียงเคี้ยวอยู่หลังบ้าน"),
                _line("Narrator EN", "en", "Three in the morning, and somebody in this village is eating."),
            ]),
            _scene(2, "Bua is not well", ["Bua", "Mor Tham"], [
                _line("Bua", "th", "ข้อยบ่ได้เฮ็ดหยัง ข้อยกะบ่ฮู้ว่าเป็นหยัง"),
                _line("Mor Tham", "th", "ตาเจ้าเปลี่ยนไปแล้ว มันบ่แม่นเจ้าที่มองข้อยอยู่"),
            ]),
            _scene(3, "Livestock first", ["Mor Tham", "Narrator EN"], [
                _line("Narrator EN", "en", "Buffalo found hollow. No wound anywhere on them."),
                _line("Mor Tham", "th", "ปอบมันกินตับกินไต บ่ได้กินเนื้อ"),
            ]),
            _scene(4, "The village decides", ["Mor Tham", "Bua"], [
                _line("Narrator EN", "en", "The oldest horror in this story is not the spirit. It is a village choosing a name."),
                _line("Bua", "th", "อย่าไล่ข้อยเด้อ ข้อยเกิดอยู่นี่"),
            ]),
            _scene(5, "Driving it out", ["Mor Tham", "Bua"], [
                _line("Mor Tham", "th", "ออกจากฮ่างเขาเดี๋ยวนี้ บ่มีบ้านให้เจ้าอยู่แล้ว"),
                _line("Bua", "th", "ถ้าข้อยออกไป ข้อยต้องไปอยู่ในใครสักคน"),
            ]),
            _scene(6, "Who is eating tonight", ["Mor Tham", "Narrator EN"], [
                _line("Narrator EN", "en", "They burned the house. The dying stopped for a year. Then it started one village over."),
                _line("Mor Tham", "th", "ปอบมันบ่ตาย มันแค่ย้ายบ้าน"),
            ]),
        ],
    },
    {
        "episode": 7,
        "title": "Kuman Thong — The Golden Child",
        "thai_title": "กุมารทอง",
        "creature": "Kuman Thong",
        "logline": "A dealer buys a gold-leafed child effigy for his shop window. It brings "
                   "him money. It expects to be raised like a son.",
        "scenes": [
            _scene(1, "A small statue, smiling", ["Narrator TH", "Kuman"], [
                _line("Narrator TH", "th", "รูปเด็กปิดทอง นั่งยิ้มอยู่ในตู้กระจก"),
                _line("Narrator EN", "en", "A gold-leafed child, smiling in a glass case. Someone fed it this morning."),
            ]),
            _scene(2, "Khun Anan makes a purchase", ["Khun Anan", "Narrator EN"], [
                _line("Khun Anan", "th", "แค่ของเก่า ขายต่อได้ราคาดี"),
                _line("Narrator EN", "en", "The seller told him the rules three times. He heard them as sales patter."),
            ]),
            _scene(3, "The luck arrives", ["Khun Anan", "Kuman"], [
                _line("Narrator EN", "en", "Four buyers in a week. A debt forgiven. A rival's shop burns down."),
                _line("Kuman", "th", "พ่อครับ ผมช่วยแล้วนะ"),
            ]),
            _scene(4, "It wants sweets and a name", ["Kuman", "Khun Anan"], [
                _line("Kuman", "th", "หิว... วันนี้ยังไม่ได้กินเลย"),
                _line("Khun Anan", "th", "มันเป็นแค่รูปปั้น รูปปั้นมันไม่กิน"),
            ]),
            _scene(5, "What he skipped", ["Kuman", "Khun Anan"], [
                _line("Kuman", "th", "พ่อลืมผม สามวันแล้วที่พ่อลืมผม"),
                _line("Khun Anan", "th", "เอาไปคืนวัด เอาไปเดี๋ยวนี้!"),
            ]),
            _scene(6, "Returned to the temple", ["Narrator EN", "Kuman"], [
                _line("Narrator EN", "en", "The temple takes them in. Shelves of small gold children, all of them fed daily, "
                                           "by monks, forever, because stopping is the dangerous part."),
                _line("Kuman", "th", "ผมรอได้ครับ ผมรอเก่ง"),
            ]),
        ],
    },
    {
        "episode": 8,
        "title": "Phi Am — The Weight on Your Chest",
        "thai_title": "ผีอำ",
        "creature": "Phi Am",
        "logline": "A student in a cheap Bangkok apartment wakes up every night at 3:14, "
                   "awake, aware, and unable to move.",
        "scenes": [
            _scene(1, "3:14 a.m.", ["Ploy", "Narrator EN"], [
                _line("Narrator EN", "en", "Awake. Eyes open. Nothing below the neck answers."),
                _line("Ploy", "th", "ขยับไม่ได้... ขยับไม่ได้เลย"),
            ]),
            _scene(2, "The cheapest room in the building", ["Ploy", "Thai Old Man"], [
                _line("Thai Old Man", "th", "ห้องนี้ถูกกว่าห้องอื่นเพราะอะไร หนูไม่ถามเหรอ"),
                _line("Ploy", "th", "หนูนอนคนเดียว แต่ที่นอนมันยุบสองรอย"),
            ]),
            _scene(3, "It has weight", ["Ploy", "Narrator EN"], [
                _line("Ploy", "th", "มันนั่งทับอยู่ตรงอก ฉันหายใจไม่ออก"),
                _line("Narrator EN", "en", "Sleep paralysis, says the doctor. A word for it is not a cure for it."),
            ]),
            _scene(4, "Learning to see it", ["Ploy"], [
                _line("Ploy", "th", "ถ้าฉันมองไปทางขวาสุด ฉันจะเห็นเข่ามัน"),
                _line("Narrator EN", "en", "Rule of Phi Am: do not let it know you can see it."),
            ]),
            _scene(5, "The finger", ["Ploy", "Thai Old Man"], [
                _line("Thai Old Man", "th", "ขยับนิ้วก้อยให้ได้นิ้วเดียว แล้วมันจะปล่อย"),
                _line("Ploy", "th", "หนึ่ง... นิ้ว... เดียว..."),
            ]),
            _scene(6, "Bruises", ["Ploy", "Narrator EN"], [
                _line("Narrator EN", "en", "She moved out. She sleeps fine now. The bruises on her chest took three weeks to fade."),
                _line("Ploy", "th", "ห้องนั้นมีคนใหม่เข้าไปอยู่แล้ว"),
            ]),
        ],
    },
    {
        "episode": 9,
        "title": "Kong Koi — One Leg, One Thirst",
        "thai_title": "กองกอย",
        "creature": "Kong Koi",
        "logline": "Two rangers camp deep in the forest. Something calls its own name in "
                   "the dark, and it is counting the sleepers.",
        "scenes": [
            _scene(1, "Kok-koi, kok-koi", ["Narrator TH"], [
                _line("Narrator TH", "th", "กอง... กอย... กอง... กอย..."),
                _line("Narrator EN", "en", "It calls its own name. That is how you know it is close enough."),
            ]),
            _scene(2, "Two hammocks", ["Ranger Wit", "Somchai"], [
                _line("Ranger Wit", "th", "คืนนี้นอนคนละเปล อย่านอนแยกกันไกล"),
                _line("Somchai", "th", "ป่าแถบนี้เงียบผิดปกติว่ะ"),
            ]),
            _scene(3, "One footprint", ["Somchai", "Ranger Wit"], [
                _line("Somchai", "th", "รอยเท้ามันมีข้างเดียว แล้วมันเดินตรงมาเลย"),
                _line("Narrator EN", "en", "One leg. It hops. Sound of a single heavy step, then nothing, then a single heavy step."),
            ]),
            _scene(4, "It drinks from the toes", ["Ranger Wit", "Narrator EN"], [
                _line("Narrator EN", "en", "It does not bite the throat. It takes the big toe and drinks from there, "
                                           "quietly, while you sleep through it."),
                _line("Ranger Wit", "th", "เอาใบไม้คลุมเท้าไว้ อย่าให้มันเห็นนิ้วเท้า"),
            ]),
            _scene(5, "Sleep two, wake one", ["Ranger Wit", "Somchai"], [
                _line("Ranger Wit", "th", "มึงตื่นอยู่ใช่ไหม ตอบกูหน่อย"),
                _line("Somchai", "th", "ตื่น... แต่กูขยับไม่ได้แล้ว"),
            ]),
            _scene(6, "Morning count", ["Ranger Wit", "Narrator EN"], [
                _line("Narrator EN", "en", "Old rule of the forest camps: never sleep in an even number. "
                                           "Something out there is also counting."),
                _line("Ranger Wit", "th", "กูเดินออกมาคนเดียว แต่กูได้ยินสองเสียงตามหลังตลอดทาง"),
            ]),
        ],
    },
    {
        "episode": 10,
        "title": "Nang Ta-khian — The Tree That Screamed",
        "thai_title": "นางตะเคียน",
        "creature": "Nang Ta-khian",
        "logline": "A highway needs to go through a two-hundred-year-old takhian tree. "
                   "The tree has been wearing ribbons since before the road existed.",
        "scenes": [
            _scene(1, "Ribbons in the headlights", ["Narrator TH", "Nang Ta-khian"], [
                _line("Narrator TH", "th", "ต้นตะเคียนต้นนั้น ผูกผ้าสีไว้เต็มลำต้น"),
                _line("Narrator EN", "en", "Every ribbon is somebody's apology, or somebody's request."),
            ]),
            _scene(2, "The survey line", ["Foreman Krit"], [
                _line("Foreman Krit", "th", "เส้นทางมันผ่ากลางต้นพอดี ย้ายไม่ได้ งบมันล็อกแล้ว"),
                _line("Narrator EN", "en", "Three crews quit before the machines even arrived."),
            ]),
            _scene(3, "The woman by the road at night", ["Nang Ta-khian", "Foreman Krit"], [
                _line("Nang Ta-khian", "th", "อย่าเพิ่งตัดเลยนะ ขอฉันอีกสักหน่อย"),
                _line("Foreman Krit", "th", "เมื่อคืนมีผู้หญิงยืนอยู่กลางถนน ผมเบรกไม่ทัน แต่ไม่มีเสียงชน"),
            ]),
            _scene(4, "The saw stalls", ["Foreman Krit", "Narrator EN"], [
                _line("Narrator EN", "en", "Two chainsaws seized. One man's arm broke. The cut in the trunk wept red."),
                _line("Foreman Krit", "th", "ไม่ใช่ยางไม้ ผมรู้ว่ายางไม้เป็นยังไง"),
            ]),
            _scene(5, "The ceremony", ["Phra Sombat", "Nang Ta-khian"], [
                _line("Phra Sombat", "th", "ขอขมา แล้วนิมนต์ท่านย้ายไปอยู่ที่ใหม่ ไม่ใช่ไล่"),
                _line("Nang Ta-khian", "th", "ฉันจะไป แต่ฉันจะจำถนนเส้นนี้ไว้"),
            ]),
            _scene(6, "The boat at the temple", ["Narrator EN", "Nang Ta-khian"], [
                _line("Narrator EN", "en", "They carved the trunk into a boat and gave it to a temple. People still bring it "
                                           "dresses. People still ask it for lottery numbers. Sometimes they win."),
                _line("Nang Ta-khian", "th", "ถ้าเธอขอ ฉันให้ แต่ของทุกอย่างมันมีราคา"),
            ]),
        ],
    },
]


def get_episode(number):
    for ep in EPISODES:
        if ep["episode"] == number:
            return ep
    raise KeyError(f"No episode {number}")


def iter_lines(episodes=None):
    """Yield (episode, scene, index, line) for every VO line."""
    for ep in episodes or EPISODES:
        for sc in ep["scenes"]:
            for i, line in enumerate(sc["vo"], start=1):
                yield ep, sc, i, line
