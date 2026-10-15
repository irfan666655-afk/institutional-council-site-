"""Assemble the Week-1 posting queue: numbered folders, media, caption.txt, schedule.csv, README."""
import shutil, pathlib, csv

S = pathlib.Path("/tmp/claude-0/-home-claude/ee3cde47-b1ef-53af-8c44-9324be7079bc/scratchpad")
Q, PNG, OLD, REEL = S / "GoldCouncil_Queue_Week1", S / "png", S / "queue_png", S / "reel/out"
shutil.rmtree(Q, ignore_errors=True); Q.mkdir()
DISC = "Education only. Not financial advice."

queue = [
 ("01", "Fri 16 Oct 2026", "09:55", "Post", "Something is shrinking", [OLD / "P1-Shrinking.png"],
  f"""Every year, something shrinks.

No vote. No headline. Just a ruler that gets a little shorter, and a whole life measured with it.

What do you think it is? One word in the comments.

From Escape the Matrix · coming soon
{DISC}
#EscapeTheMatrix #TheGoldCouncil #Gold #Inflation #PurchasingPower""",
  "First comment to pin: Hint: you were paid in it this month."),
 ("02", "Sat 17 Oct 2026", "17:55", "Reel", "Case File 001 · The night the anchor was cut", [REEL / "reel1.mp4", PNG / "R1-Cover.png"],
  f"""Case File 001.

One Sunday night in 1971, the link between the US dollar and gold was cut.
It was called temporary. Watch till the end.

{DISC}
#EscapeTheMatrix #TheGoldCouncil #Gold #MoneyHistory #XAUUSD""",
  "First comment to pin: Fragment 01 on our grid has the date. Start there."),
 ("03", "Sun 18 Oct 2026", "17:55", "Post", "The arithmetic", [OLD / "P2-Arithmetic.png"],
  f"""$100 from 1913 buys about $2.95 of goods today.

Closer to home: one tola of gold cost Rs 43 in 1950. On 12 Oct 2026 it was Rs 437,500.
The gold didn't get ten thousand times better. The ruler changed.

Sources: US CPI (Minneapolis Fed, BLS); SBP; market tola rate 12 Oct 2026; Grand Atlas II (computed)
{DISC}
#EscapeTheMatrix #TheGoldCouncil #GoldPricePakistan #Tola #XAUUSD""",
  "First comment to pin: What did a tola cost when your parents married? Tell us the year and the price."),
 ("04", "Mon 19 Oct 2026", "09:55", "Carousel", "Why we exist (4 slides)", [OLD / f"C2-Why-{i}.png" for i in range(1, 5)],
  f"""The matrix isn't a conspiracy. It's the money illusion.

Four slides: the raise that wasn't, the rupee close to home, and Escape Rule 01. Swipe, then save it.

{DISC}
#EscapeTheMatrix #TheGoldCouncil #MoneyIllusion #Gold #PersonalFinance""",
  "First comment to pin: Rule 01 is free. Rules 02 to 10 are in the documentary."),
 ("05", "Tue 20 Oct 2026", "17:55", "Reel", "Case File 002 · Your money has a ruler", [REEL / "reel2.mp4", PNG / "R2-Cover.png"],
  f"""Your money has a ruler. 19 seconds on why it keeps shrinking, and the one ruler we check it against.

Escape Rule 01: keep two sets of books.

Source for the rupee rate: State Bank of Pakistan interbank, Oct 2026
{DISC}
#EscapeTheMatrix #TheGoldCouncil #Gold #Tola #PKR""",
  "First comment to pin: Book 1 is rupees. What would you put in Book 2?"),
 ("06", "Wed 21 Oct 2026", "09:55", "Post", "Myth vs record", [OLD / "P3-Myth.png"],
  f"""Myth: banks lend out your deposits.
Record: in 2014 the Bank of England wrote that whenever a bank makes a loan, it creates a matching deposit.

New money is typed into existence. Who gets it first matters. The documentary shows how.

Source: Bank of England Quarterly Bulletin 2014 Q1, "Money creation in the modern economy"
{DISC}
#EscapeTheMatrix #TheGoldCouncil #MoneyCreation #Banking #Gold""",
  "First comment to pin: Did you learn the myth version in school? Yes or no."),
 ("07", "Thu 22 Oct 2026", "09:55", "Carousel", "Four things before the file opens (5 slides)", [PNG / f"CF-{i}.png" for i in range(1, 6)],
  f"""Four things to know before the file opens: 1971, the shrinking ruler, what we do, and the one rule we keep.

Save this. You will want it when Escape the Matrix drops.

{DISC}
#EscapeTheMatrix #TheGoldCouncil #Gold #XAUUSD #FinancialEducation""",
  "First comment to pin: Which slide surprised you most? 1, 2, 3 or 4?"),
 ("08", "Fri 23 Oct 2026", "09:55", "Carousel", "Who we are (4 slides)", [OLD / f"C1-Who-{i}.png" for i in range(1, 5)],
  f"""Who is The Gold Council?

A research council, not a signal shop. Every number sourced, every call scored, and four lines we won't cross.

{DISC}
#TheGoldCouncil #EscapeTheMatrix #GoldResearch #XAUUSD #Gold""",
  "First comment to pin: Line 04 matters most to us. If we ever earn from a partner, you will hear it from us first."),
 ("09", "Sat 24 Oct 2026", "09:55", "Post", "No one knows the hour", [OLD / "P4-Hour.png"],
  f"""Six traditions. One warning: no one knows the hour.

We will never give you a date for the end of anything. We will give you a way to prepare.

Sources: Qur'an 7:187 · Matthew 24:36 · Sanhedrin 97b · Vishnu Purana · Majjhima Nikaya 63 · Japji Sahib, Pauri 21
{DISC}
#EscapeTheMatrix #TheGoldCouncil #Faith #Gold #Preparation""",
  "First comment to pin: Read with respect. Referenced exactly. Kept apart from market signals."),
]
story = ("S1", "Fri 16 Oct 2026", "13:00", "Story (manual)", "Quick poll: what did 1971 do to your money?", [PNG / "S1-Poll.png"],
         "No caption. Post from the Instagram app and add the Poll sticker in the dashed box: YES / NO IDEA.", "")

rows = []
for num, day, time, kind, title, media, caption, comment in queue + [story]:
    d = Q / f"{num}_{day.split()[0]}{day.split()[1]}{day.split()[2]}_{kind.split()[0]}"
    d.mkdir()
    for i, m in enumerate(media, 1):
        ext = m.suffix
        if kind == "Reel":
            name = "video.mp4" if ext == ".mp4" else "cover.png"
        elif kind == "Carousel":
            name = f"slide{i}{ext}"
        else:
            name = f"image{ext}"
        shutil.copy(m, d / name)
    (d / "caption.txt").write_text(caption + ("\n\n---\n" + comment if comment else "") + "\n")
    rows.append([num, day, time + " PKT", kind, title, d.name, len(media)])
with open(Q / "schedule.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["#", "day", "time", "type", "title", "folder", "files"]); w.writerows(rows)
(Q / "README.txt").write_text("""THE GOLD COUNCIL · WEEK 1 QUEUE (16 to 24 Oct 2026)

Post in number order, one per day. Times are Pakistan time and come from Metricool's best-time data:
weekday posts 09:55, reels 17:55, Sunday 17:55.

Each folder holds the media plus caption.txt. The line after --- in caption.txt is the first comment to post and pin.
S1 is a story: post it from the Instagram app so you can add the poll sticker.

Grid rows this week builds (left to right as they appear on the profile):
  row 1: 03 Arithmetic | 02 Reel Case File 001 | 01 Shrinking
  row 2: 06 Myth | 05 Reel Case File 002 | 04 Why we exist
  row 3: 09 No one knows the hour | 08 Who we are | 07 Four things

No Escape the Matrix countdown is included, as asked.
""")
print("\n".join(",".join(map(str, r)) for r in rows))
