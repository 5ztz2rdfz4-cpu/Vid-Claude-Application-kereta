<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Anton"; src: url("assets/fonts/anton.woff2") format("woff2"); font-weight: 400; }
      @font-face { font-family: "Montserrat"; src: url("assets/fonts/montserrat.woff2") format("woff2"); font-weight: 100 900; }
      :root {
        --ground: #08090c;
        --panel: #12141a;
        --panel-2: #1a1d25;
        --line: #2a2e38;
        --ink: #ffffff;
        --mute: #9aa0ab;
        --accent: #ffd60a;
        --red: #e5242c;
        --green: #22c55e;
        --font-display: "Anton", sans-serif;
        --font-body: "Montserrat", sans-serif;
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: var(--ground); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: var(--font-body); color: var(--ink); }
      .clip { position: absolute; inset: 0; }
      .abs { position: absolute; }
      .abs.clip { right: auto; bottom: auto; }

      /* ---------- info background ---------- */
      #infoBg { background:
          radial-gradient(900px 500px at 50% -80px, rgba(255,214,10,.22), transparent 70%),
          radial-gradient(700px 700px at 50% 1250px, rgba(255,214,10,.08), transparent 70%),
          linear-gradient(180deg, #0d0f14 0%, #06070a 100%); opacity: 0; }
      #infoBg .grid { position:absolute; inset:0; opacity:.07;
          background-image: linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px);
          background-size: 60px 60px; }

      /* ---------- camera ---------- */
      #camPip { transform-origin: 0 0; clip-path: inset(0px 0px 0px 0px round 0px); }
      #camZoom { transform-origin: 460px 740px; }
      #talk { width: 1080px; height: 1920px; object-fit: cover; display: block; }
      #pipFrame { left: 280px; top: 940px; width: 520px; height: 560px; border-radius: 40px;
          border: 5px solid var(--accent); box-shadow: 0 0 0 10px rgba(255,214,10,.12), 0 30px 80px rgba(0,0,0,.6); opacity: 0; }
      #vignette { opacity: 0; background: linear-gradient(180deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 28%, rgba(0,0,0,0) 55%, rgba(0,0,0,.45) 100%); }

      /* ---------- generic UI ---------- */
      .pill { display:inline-block; font: 800 26px/1 var(--font-body); letter-spacing:.12em; text-transform:uppercase;
          color:#0b0b0b; background: var(--accent); padding: 12px 22px; border-radius: 10px; }
      .titlebox { background: rgba(10,11,15,.88); border: 2px solid rgba(255,255,255,.08); border-radius: 26px;
          padding: 30px 44px 34px; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,.45); }
      .disp { font-family: var(--font-display); text-transform: uppercase; line-height: .98; letter-spacing: .01em; }
      .y { color: var(--accent); }
      .sub { font: 700 30px/1.25 var(--font-body); color: #d9dce2; }

      /* ---------- section header ---------- */
      .hdr { left: 60px; top: 150px; width: 900px; display:flex; align-items:center; gap: 26px; }
      .hdr .num { font-family: var(--font-display); font-size: 92px; line-height: 1; color: var(--accent);
          border: 5px solid var(--accent); border-radius: 18px; padding: 4px 16px 8px; }
      .hdr h2 { font-family: var(--font-display); font-weight: 400; font-size: 64px; line-height: 1; text-transform: uppercase; }
      .hdr p { font: 600 26px/1.3 var(--font-body); color: var(--mute); margin-top: 8px; }

      /* ---------- S1 spec cards ---------- */
      .spec { left: 60px; width: 900px; height: 150px; background: var(--panel); border: 2px solid var(--line);
          border-radius: 24px; display:flex; align-items:center; padding: 0 34px; gap: 30px; opacity: 0; }
      .spec .n { width: 74px; height: 74px; border-radius: 50%; background: var(--accent); color:#0b0b0b;
          font: 400 44px/74px var(--font-display); text-align:center; flex: none; }
      .spec h3 { font-family: var(--font-display); font-weight:400; font-size: 58px; line-height: 1; }
      .spec p { font: 600 25px/1.2 var(--font-body); color: var(--mute); margin-top: 6px; }
      .spec .bar { margin-left:auto; display:flex; gap:8px; }
      .spec .bar i { width: 18px; height: 48px; border-radius: 6px; background: var(--line); display:block; }
      .spec .bar i.f { background: var(--accent); }
      .spec.hot { border-color: var(--accent); box-shadow: 0 0 0 6px rgba(255,214,10,.12); }

      /* ---------- S2 transmission cards ---------- */
      .tcard { top: 320px; width: 432px; height: 560px; background: var(--panel); border: 2px solid var(--line);
          border-radius: 30px; overflow: hidden; opacity: 0; }
      .tcard .tags { position:absolute; left: 28px; right: 28px; top: 30px; display:flex; flex-wrap:wrap; gap: 10px; }
      .tag { font: 800 22px/1 var(--font-body); letter-spacing:.08em; padding: 12px 16px; border-radius: 10px;
          background: var(--panel-2); border: 2px solid var(--line); color: #fff; opacity: 0; }
      .tcard .big { position:absolute; left:0; right:0; top: 170px; text-align:center; font-family: var(--font-display);
          font-size: 190px; line-height: 1; color: var(--accent); }
      .tcard .q { position:absolute; left:0; right:0; top: 170px; text-align:center; font-family: var(--font-display);
          font-size: 190px; line-height: 1; color: #2c303a; }
      .tcard .desc { position:absolute; left: 28px; right: 28px; bottom: 32px; text-align:center;
          font: 700 26px/1.25 var(--font-body); color: #d9dce2; opacity: 0; }
      .tcard .gear { position:absolute; right: -60px; bottom: -60px; width: 220px; height: 220px; opacity: .07; }
      #vs { left: 470px; top: 540px; width: 100px; height: 100px; border-radius: 50%; background: var(--accent);
          color: #0b0b0b; font: 400 46px/100px var(--font-display); text-align: center; opacity: 0;
          box-shadow: 0 0 0 10px #06070a; }

      /* ---------- S4 driving style ---------- */
      .row { left: 60px; width: 900px; height: 170px; background: var(--panel); border: 2px solid var(--line);
          border-radius: 26px; display:flex; align-items:center; padding: 0 30px; gap: 26px; opacity: 0; }
      .row .ic { width: 100px; height: 100px; border-radius: 22px; background: var(--panel-2); flex:none;
          display:flex; align-items:center; justify-content:center; }
      .row h3 { font-family: var(--font-display); font-weight:400; font-size: 54px; line-height: 1; }
      .row p { font: 600 25px/1.25 var(--font-body); color: var(--mute); margin-top: 6px; }
      .row .badge { margin-left:auto; flex:none; width: 170px; height: 110px; border-radius: 20px; background: var(--accent);
          color:#0b0b0b; font: 400 70px/110px var(--font-display); text-align:center; opacity: 0; }
      .row .arrow { flex:none; opacity: 0; }
      #meter { left: 60px; top: 720px; width: 900px; height: 170px; opacity: 0; }
      #meter .track { position:absolute; left: 30px; right: 30px; top: 70px; height: 22px; border-radius: 11px;
          background: linear-gradient(90deg, #22c55e, #ffd60a 55%, #e5242c); }
      #meter .lbl { position:absolute; top: 0; font: 800 24px/1 var(--font-body); letter-spacing:.12em; color: var(--mute); }
      #meter .lbl b { color: #fff; font-family: var(--font-display); font-weight: 400; font-size: 40px; letter-spacing: .02em; margin-left: 10px; }
      #needle { position:absolute; left: 450px; top: 50px; width: 0; height: 0; }
      #needle i { position:absolute; left: -16px; top: 0; width: 32px; height: 62px; border-radius: 10px; background: #fff;
          box-shadow: 0 6px 20px rgba(0,0,0,.6); border: 4px solid #0b0b0b; display:block; }
      #meter .cap { position:absolute; left: 30px; right: 30px; top: 118px; display:flex; justify-content: space-between;
          font: 700 24px/1.2 var(--font-body); color: var(--mute); }

      /* ---------- captions ---------- */
      #caps { left: 40px; width: 1000px; top: 1180px; height: 120px; }
      .cg { position:absolute; left:0; right:0; top:0; text-align:center; opacity:0; visibility:hidden; }
      .w { display:inline-block; font: 900 58px/1.15 var(--font-body); color:#fff; text-transform: uppercase;
          padding: 2px 12px 6px; margin: 0 12px; border-radius: 12px; letter-spacing: -.01em;
          -webkit-text-stroke: 3px #0b0b0b; paint-order: stroke fill;
          text-shadow: 0 6px 0 rgba(0,0,0,.55), 0 10px 30px rgba(0,0,0,.6); }
      .w.key { color: var(--accent); }

      /* ---------- hook ---------- */
      #hook { left: 70px; top: 150px; width: 940px; text-align: center; }
      #hook .disp { font-size: 112px; white-space: nowrap; }
      #sticker { left: 200px; top: 545px; background: var(--red); color: #fff; font: 400 66px/1 var(--font-display);
          padding: 16px 30px 22px; border-radius: 14px; transform: rotate(-6deg); box-shadow: 0 16px 40px rgba(0,0,0,.45);
          text-transform: uppercase; opacity: 0; }

      /* ---------- b-roll ---------- */
      #broll { opacity: 0; overflow: hidden; }
      #broll .bgimg { position:absolute; inset:-80px; background: url("assets/saga.webp") center/cover; filter: blur(40px) brightness(.45) saturate(1.2); }
      #broll .car { position:absolute; left: -330px; top: 640px; width: 1740px; height: 979px;
          background: url("assets/saga.webp") center/cover; border-radius: 0; }
      #broll .fade { position:absolute; inset:0; background: linear-gradient(180deg, rgba(6,7,10,.95) 0%, rgba(6,7,10,.2) 34%, rgba(6,7,10,0) 60%, rgba(6,7,10,.75) 100%); }
      #brollTxt { left: 0; width: 1080px; top: 190px; text-align:center; }
      #brollTxt .row2 { display:flex; align-items:center; justify-content:center; gap: 34px; margin-top: 26px; }
      #brollTxt .disp { font-size: 190px; }
      #brollTxt .vsb { width: 120px; height: 120px; border-radius: 50%; background: var(--accent); color:#0b0b0b;
          font: 400 58px/120px var(--font-display); text-align:center; }

      /* ---------- full-cam titles ---------- */
      .ftitle { left: 90px; top: 170px; width: 900px; }
      .ftitle .disp { font-size: 104px; }

      /* ---------- CTA ---------- */
      #ctaForm { left: 110px; top: 160px; width: 860px; text-align:center; opacity: 0; }
      #ctaForm .banner { background: var(--accent); color:#0b0b0b; font: 400 92px/1 var(--font-display);
          padding: 24px 30px 30px; border-radius: 22px; text-transform: uppercase; box-shadow: 0 20px 60px rgba(0,0,0,.5); }
      #ctaForm .arrow { display:block; margin: 18px auto 0; width: 90px; height: 90px; }
      #ctaForm .note { margin-top: 18px; display:inline-block; background: rgba(10,11,15,.88); border-radius: 18px;
          padding: 20px 30px; font: 700 32px/1.3 var(--font-body); color:#fff; }

      /* ---------- end card ---------- */
      #endCard { background:
          radial-gradient(800px 600px at 50% 40%, rgba(255,214,10,.16), transparent 70%), #06070a; opacity: 0; }
      #endCard .car { position:absolute; left: -200px; top: 1150px; width: 1480px; height: 833px;
          background: url("assets/saga.webp") center/cover; opacity: .32;
          -webkit-mask-image: linear-gradient(180deg, transparent 0%, #000 40%, #000 70%, transparent 100%); mask-image: linear-gradient(180deg, transparent 0%, #000 40%, #000 70%, transparent 100%); }
      #endInner { left: 0; width: 1080px; top: 560px; text-align: center; }
      #endInner .small { font: 800 30px/1 var(--font-body); letter-spacing: .2em; color: #d9dce2; }
      #endInner .follow { font-family: var(--font-display); font-size: 250px; line-height: 1; margin-top: 18px; }
      #endInner .tl { font: 700 38px/1.3 var(--font-body); margin-top: 10px; }
      #endInner .btn { display:inline-block; margin-top: 50px; background: var(--accent); color:#0b0b0b;
          font: 400 60px/1 var(--font-display); padding: 22px 40px 28px; border-radius: 16px; text-transform: uppercase; }

      /* ---------- progress ---------- */
      #prog { left: 0; top: 0; height: 10px; width: 1080px; background: var(--accent); transform-origin: 0 0; transform: scaleX(0);
          box-shadow: 0 0 20px rgba(255,214,10,.6); }
      #flash { background: #fff; opacity: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{TOTAL}}" data-width="1080" data-height="1920">

      <!-- background for infographic (PiP) mode -->
      <div id="infoBg" class="clip" data-start="0" data-duration="{{TOTAL}}" data-track-index="0"><div class="grid"></div></div>

      <!-- talking head: zoom wrapper inside PiP wrapper -->
      <div id="camPip" class="clip">
        <div id="camZoom" class="clip">
          <video id="talk" src="assets/talk.mp4" data-start="0" data-duration="{{TALK}}" data-has-audio="true" data-volume="1" data-track-index="1" playsinline></video>
        </div>
      </div>
      <div id="vignette" class="clip" data-start="0" data-duration="{{TALK}}" data-track-index="2"></div>
      <div id="pipFrame" class="abs clip" data-start="0" data-duration="{{TALK}}" data-track-index="2"></div>

      <!-- ===== HOOK ===== -->
      <div id="hook" class="abs clip" data-start="0" data-duration="2.6" data-track-index="6">
        <div class="pill" id="hookPill">Tips beli Proton Saga</div>
        <div class="titlebox" style="margin-top:22px">
          <div class="disp" id="hk1">Saga MC3</div>
          <div class="disp y" id="hk2">gear tak sama?!</div>
        </div>
      </div>
      <div id="sticker" class="abs clip" data-start="0" data-duration="2.6" data-track-index="7">Jangan salah pilih!</div>

      <!-- ===== B-ROLL ===== -->
      <div id="broll" class="clip" data-start="2.4" data-duration="2.9" data-track-index="5">
        <div class="bgimg"></div>
        <div class="car" id="brCar"></div>
        <div class="fade"></div>
        <div id="brollTxt" class="abs">
          <div class="pill">Proton Saga MC3</div>
          <div class="row2">
            <div class="disp" id="br4">4AT</div>
            <div class="vsb" id="brvs">VS</div>
            <div class="disp y" id="brc">CVT</div>
          </div>
          <div class="sub" id="brsub" style="margin-top:14px">Satu model &middot; dua jenis gear</div>
        </div>
      </div>

      <!-- ===== S1: 01 3 SPEK ===== -->
      <div id="s1" class="clip" data-start="5.0" data-duration="5.3" data-track-index="6">
        <div class="hdr abs" id="s1h">
          <div class="num">01</div>
          <div><h2>3 Spek Saga MC3</h2><p>Satu model, tiga pilihan</p></div>
        </div>
        <div class="spec abs" id="sp1" style="top:340px"><div class="n">1</div><div><h3>Standard</h3><p>Spek asas &middot; harga paling mampu</p></div><div class="bar"><i class="f"></i><i></i><i></i></div></div>
        <div class="spec abs" id="sp2" style="top:520px"><div class="n">2</div><div><h3>Executive</h3><p>Tambah ciri &amp; keselesaan</p></div><div class="bar"><i class="f"></i><i class="f"></i><i></i></div></div>
        <div class="spec abs hot" id="sp3" style="top:700px"><div class="n">3</div><div><h3>Premium</h3><p>Spek paling lengkap</p></div><div class="bar"><i class="f"></i><i class="f"></i><i class="f"></i></div></div>
      </div>

      <!-- ===== S2: 02 TRANSMISI ===== -->
      <div id="s2" class="clip" data-start="9.9" data-duration="13.5" data-track-index="6">
        <div class="hdr abs" id="s2h">
          <div class="num">02</div>
          <div><h2>2 Jenis Transmisi</h2><p>Lain spek, lain gearbox</p></div>
        </div>
        <div class="tcard abs" id="tc1" style="left:60px">
          <div class="tags"><span class="tag" id="tgS">STANDARD</span><span class="tag" id="tgE">EXECUTIVE</span></div>
          <div class="q" id="q1">?</div>
          <div class="big" id="b1" style="opacity:0">4AT</div>
          <div class="desc" id="d1">Automatik 4-kelajuan<br/><span class="y">Tarikan lebih &ldquo;direct&rdquo;</span></div>
          <svg class="gear" viewBox="0 0 100 100"><path fill="#fff" d="M43 2h14l2 12 8 3 10-7 10 10-7 10 3 8 12 2v14l-12 2-3 8 7 10-10 10-10-7-8 3-2 12H43l-2-12-8-3-10 7-10-10 7-10-3-8-12-2V43l12-2 3-8-7-10 10-10 10 7 8-3z"/><circle cx="50" cy="50" r="16" fill="#12141a"/></svg>
        </div>
        <div class="tcard abs" id="tc2" style="left:528px">
          <div class="tags"><span class="tag" id="tgP" style="border-color:#ffd60a">PREMIUM</span></div>
          <div class="q" id="q2">?</div>
          <div class="big" id="b2" style="opacity:0">CVT</div>
          <div class="desc" id="d2">Continuously Variable<br/><span class="y">Gerak lebih &ldquo;smooth&rdquo;</span></div>
          <svg class="gear" viewBox="0 0 100 100"><path fill="#fff" d="M43 2h14l2 12 8 3 10-7 10 10-7 10 3 8 12 2v14l-12 2-3 8 7 10-10 10-10-7-8 3-2 12H43l-2-12-8-3-10 7-10-10 7-10-3-8-12-2V43l12-2 3-8-7-10 10-10 10 7 8-3z"/><circle cx="50" cy="50" r="16" fill="#12141a"/></svg>
        </div>
        <div id="vs" class="abs">VS</div>
      </div>

      <!-- ===== S3: MANA LAGI BAGUS (full cam) ===== -->
      <div id="t3a" class="ftitle abs clip" data-start="23.3" data-duration="3.2" data-track-index="6">
        <div class="titlebox"><div class="disp">Mana satu</div><div class="disp y">lagi bagus?</div></div>
      </div>
      <div id="t3b" class="ftitle abs clip" data-start="26.3" data-duration="2.9" data-track-index="6">
        <div class="titlebox"><div class="pill" style="margin-bottom:14px">Jawapannya</div><div class="disp" style="font-size:86px">Ikut cara</div><div class="disp y" style="font-size:86px">pemanduan korang</div></div>
      </div>

      <!-- ===== S4: 03 GAYA PEMANDUAN ===== -->
      <div id="s4" class="clip" data-start="29.0" data-duration="10.5" data-track-index="6">
        <div class="hdr abs" id="s4h">
          <div class="num">03</div>
          <div><h2>Pilih ikut gaya bawa</h2><p>Cara pemanduan tentukan gear</p></div>
        </div>
        <div class="row abs" id="r1" style="top:330px">
          <div class="ic"><svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#e5242c" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22a8 8 0 0 0 8-8c0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-4-3 2-7 5-7 8a8 8 0 0 0 8 8z"/></svg></div>
          <div><h3>Kaki lenjan</h3><p>Nak tarikan &amp; kepuasan</p></div>
          <svg class="arrow" id="ar1" width="54" height="40" viewBox="0 0 54 40"><path d="M2 20h44M32 6l14 14-14 14" fill="none" stroke="#ffd60a" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <div class="badge" id="bd1">4AT</div>
        </div>
        <div class="row abs" id="r2" style="top:525px">
          <div class="ic"><svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/><path d="M2 21c0-3 1.9-5.4 5.2-6"/></svg></div>
          <div><h3>Santai &amp; rilek</h3><p>Pandu tenang, lebih selesa</p></div>
          <svg class="arrow" id="ar2" width="54" height="40" viewBox="0 0 54 40"><path d="M2 20h44M32 6l14 14-14 14" fill="none" stroke="#ffd60a" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <div class="badge" id="bd2">CVT</div>
        </div>
        <div id="meter" class="abs">
          <div class="lbl" style="left:30px">SANTAI<b>CVT</b></div>
          <div class="lbl" style="right:30px"><b style="margin:0 10px 0 0">4AT</b>LAJU</div>
          <div class="track"></div>
          <div id="needle"><i></i></div>
          <div class="cap"><span>Cool &amp; smooth</span><span>Gaya pemanduan</span><span>Agresif</span></div>
        </div>
      </div>

      <!-- ===== S5: CTA (full cam) ===== -->
      <div id="t5a" class="ftitle abs clip" data-start="39.4" data-duration="3.7" data-track-index="6">
        <div class="titlebox"><div class="pill" style="margin-bottom:14px">Masih keliru?</div><div class="disp" style="font-size:88px">Saga mana yang</div><div class="disp y" style="font-size:88px">sesuai untuk korang?</div></div>
      </div>
      <div id="ctaForm" class="abs clip" data-start="42.9" data-duration="4.5" data-track-index="6">
        <div class="banner">Isi form di bawah</div>
        <svg class="arrow" id="ctaArrow" viewBox="0 0 90 90"><circle cx="45" cy="45" r="42" fill="#ffd60a"/><path d="M45 22v42M28 48l17 17 17-17" fill="none" stroke="#0b0b0b" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <div class="note">Kami bantu korang dari <span class="y">A sampai Z</span></div>
      </div>

      <!-- ===== captions ===== -->
      <div id="caps" class="abs clip" data-start="0" data-duration="{{TALK}}" data-track-index="8">
{{CAPTIONS}}
      </div>

      <!-- ===== END CARD ===== -->
      <div id="endCard" class="clip" data-start="47.2" data-duration="2.8" data-track-index="9">
        <div class="car"></div>
        <div id="endInner" class="abs">
          <div class="small" id="e1">SIMPAN VIDEO NI &amp; SHARE</div>
          <div class="follow" id="e2">FOLLOW</div>
          <div class="tl" id="e3">untuk lebih banyak <span class="y">tips kereta</span></div>
          <div class="btn" id="e4">Isi form di bawah &darr;</div>
        </div>
      </div>

      <div id="flash" class="clip" data-start="0" data-duration="{{TOTAL}}" data-track-index="10"></div>
      <div id="prog" class="abs clip" data-start="0" data-duration="{{TOTAL}}" data-track-index="10"></div>

      <!-- ===== audio ===== -->
      <audio id="music1" src="assets/music.wav" data-start="0" data-duration="47.3" data-media-start="0" data-volume="0.13" data-track-index="11"></audio>
      <audio id="music2" src="assets/music.wav" data-start="47.3" data-duration="2.7" data-media-start="47.3" data-volume="0.4" data-fade-in="0.25" data-fade-out="1.2" data-track-index="12"></audio>
{{SFX}}
    </div>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const E = "power3.out", IO = "power3.inOut";

      /* ---------- progress ---------- */
      tl.fromTo("#prog", { scaleX: 0 }, { scaleX: 1, duration: {{TOTAL}}, ease: "none" }, 0);

      /* ---------- camera modes ---------- */
      const PIP = { x: 254.8, y: 662, scale: 0.62, clipPath: "inset(449px 201px 569px 41px round 64px)" };
      const FULL = { x: 0, y: 0, scale: 1, clipPath: "inset(0px 0px 0px 0px round 0px)" };
      tl.set("#camPip", FULL, 0);
      tl.fromTo("#vignette", { opacity: 0 }, { opacity: 1, duration: 0.01 }, 0);
      tl.set("#pipFrame", { opacity: 0, scale: 0.92 }, 0);
      function toPip(t) {
        tl.to("#camPip", { ...PIP, duration: 0.55, ease: IO }, t);
        tl.to("#camZoom", { scale: 1, duration: 0.55, ease: IO }, t);
        tl.to("#infoBg", { opacity: 1, duration: 0.4 }, t);
        tl.to("#vignette", { opacity: 0, duration: 0.3 }, t);
        tl.set("#pipFrame", { scale: 0.92 }, t + 0.34);
        tl.to("#pipFrame", { opacity: 1, scale: 1, duration: 0.35, ease: E }, t + 0.35);
        tl.to("#caps", { y: 290, duration: 0.55, ease: IO }, t);
      }
      function toFull(t) {
        tl.to("#pipFrame", { opacity: 0, duration: 0.15 }, t);
        tl.to("#camPip", { ...FULL, duration: 0.55, ease: IO }, t);
        tl.to("#infoBg", { opacity: 0, duration: 0.4 }, t + 0.25);
        tl.to("#vignette", { opacity: 1, duration: 0.3 }, t + 0.3);
        tl.to("#caps", { y: 0, duration: 0.55, ease: IO }, t);
      }
      function punch(t, s, d = 0.18) { tl.to("#camZoom", { scale: s, duration: d, ease: "power4.out" }, t); }
      function drift(t, s, d) { tl.to("#camZoom", { scale: s, duration: d, ease: "sine.inOut" }, t); }

      // HOOK: punch-in on frame 1
      tl.fromTo("#camZoom", { scale: 1.32 }, { scale: 1.1, duration: 0.6, ease: "power4.out" }, 0);
      drift(0.6, 1.16, 0.9);
      punch(1.52, 1.26);
      drift(1.75, 1.2, 0.7);
      toPip(5.1);
      toFull(23.3);
      tl.set("#camZoom", { scale: 1.08 }, 23.3);
      punch(25.62, 1.24); drift(25.85, 1.1, 0.6); drift(26.5, 1.16, 2.5);
      toPip(29.1);
      toFull(39.4);
      tl.set("#camZoom", { scale: 1.06 }, 39.4);
      drift(39.5, 1.14, 3.4);
      punch(43.0, 1.28); drift(43.25, 1.16, 0.8); drift(44.1, 1.22, 3.2);

      // white flash on hard transitions
      [0, 2.45, 47.3].forEach(t => tl.fromTo("#flash", { opacity: 0.55 }, { opacity: 0, duration: 0.25, ease: "power2.out" }, t));

      /* ---------- HOOK ---------- */
      tl.fromTo("#hookPill", { y: -40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: E }, 0.05);
      tl.fromTo("#hook .titlebox", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2)" }, 0.08);
      tl.fromTo("#hk2", { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(3)" }, 0.45);
      tl.fromTo("#sticker", { scale: 2.2, opacity: 0, rotation: -14 }, { scale: 1, opacity: 1, rotation: -6, duration: 0.28, ease: "back.out(2.5)" }, 0.95);
      tl.to("#sticker", { scale: 1.06, duration: 0.25, yoyo: true, repeat: 3, ease: "sine.inOut" }, 1.25);
      tl.to(["#hook", "#sticker"], { opacity: 0, y: -30, duration: 0.2 }, 2.38);

      /* ---------- B-ROLL ---------- */
      tl.fromTo("#broll", { opacity: 0 }, { opacity: 1, duration: 0.12 }, 2.42);
      tl.fromTo("#brCar", { scale: 1.25, x: 120 }, { scale: 1.02, x: -60, duration: 2.8, ease: "sine.out" }, 2.42);
      tl.fromTo("#brollTxt .pill", { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.25, ease: E }, 2.55);
      tl.fromTo("#br4", { x: -300, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: E }, 3.3);
      tl.fromTo("#brc", { x: 300, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: E }, 3.3);
      tl.fromTo("#brvs", { scale: 0, rotation: -180 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2)" }, 3.45);
      tl.fromTo("#brsub", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3 }, 3.9);
      tl.to("#broll", { yPercent: -100, duration: 0.45, ease: "power3.in" }, 4.85);

      /* ---------- S1 ---------- */
      tl.fromTo("#s1h", { x: -80, opacity: 0 }, { x: 0, opacity: 1, duration: 0.4, ease: E }, 5.35);
      [["#sp1", 7.74], ["#sp2", 8.72], ["#sp3", 9.74]].forEach(([s, t]) => {
        tl.fromTo(s, { x: 140, opacity: 0 }, { x: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, t - 0.05);
        tl.fromTo(s + " .bar i.f", { scaleY: 0 }, { scaleY: 1, duration: 0.25, stagger: 0.07, ease: E, transformOrigin: "50% 100%" }, t + 0.15);
      });
      tl.to("#s1", { opacity: 0, x: -60, duration: 0.25 }, 10.0);

      /* ---------- S2 ---------- */
      tl.fromTo("#s2h", { x: -80, opacity: 0 }, { x: 0, opacity: 1, duration: 0.4, ease: E }, 10.05);
      tl.fromTo("#tc1", { y: 120, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "back.out(1.4)" }, 11.4);
      tl.fromTo("#tc2", { y: 120, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "back.out(1.4)" }, 11.55);
      tl.fromTo("#vs", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(3)" }, 11.75);
      tl.fromTo(".tcard .gear", { rotation: 0 }, { rotation: 180, duration: 12, ease: "none" }, 11.4);
      tl.fromTo("#tgS", { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(3)" }, 16.82);
      tl.fromTo("#tgE", { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(3)" }, 17.38);
      tl.to("#tc1", { borderColor: "#ffd60a", boxShadow: "0 0 0 8px rgba(255,214,10,.15)", duration: 0.2 }, 17.38);
      tl.to("#q1", { opacity: 0, scale: 0.5, duration: 0.15 }, 19.2);
      tl.fromTo("#b1", { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }, 19.28);
      tl.fromTo("#d1", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3 }, 19.6);
      tl.to("#tc1", { borderColor: "#2a2e38", boxShadow: "0 0 0 0px rgba(255,214,10,0)", duration: 0.2 }, 21.1);
      tl.fromTo("#tgP", { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(3)" }, 21.22);
      tl.to("#tc2", { borderColor: "#ffd60a", boxShadow: "0 0 0 8px rgba(255,214,10,.15)", duration: 0.2 }, 21.22);
      tl.to("#q2", { opacity: 0, scale: 0.5, duration: 0.15 }, 22.76);
      tl.fromTo("#b2", { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }, 22.84);
      tl.fromTo("#d2", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3 }, 23.0);
      tl.to("#s2", { opacity: 0, duration: 0.25 }, 23.15);

      /* ---------- S3 ---------- */
      tl.fromTo("#t3a .titlebox", { scale: 0.5, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.2)" }, 23.4);
      tl.to("#t3a", { opacity: 0, scale: 0.9, duration: 0.18 }, 26.3);
      tl.fromTo("#t3b .titlebox", { y: -60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "back.out(2)" }, 26.46);
      tl.to("#t3b", { opacity: 0, duration: 0.2 }, 29.0);

      /* ---------- S4 ---------- */
      tl.fromTo("#s4h", { x: -80, opacity: 0 }, { x: 0, opacity: 1, duration: 0.4, ease: E }, 29.4);
      tl.fromTo("#r1", { x: 140, opacity: 0 }, { x: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 29.7);
      tl.fromTo("#meter", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: E }, 30.2);
      tl.fromTo("#needle", { x: 0 }, { x: 330, duration: 0.7, ease: "back.out(1.4)" }, 31.08);
      tl.to("#r1", { borderColor: "#e5242c", duration: 0.2 }, 31.08);
      tl.fromTo("#ar1", { x: -30, opacity: 0 }, { x: 0, opacity: 1, duration: 0.25 }, 33.1);
      tl.fromTo("#bd1", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)" }, 33.34);
      tl.to("#r1", { borderColor: "#2a2e38", duration: 0.2 }, 34.3);
      tl.fromTo("#r2", { x: 140, opacity: 0 }, { x: 0, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }, 34.4);
      tl.to("#needle", { x: -330, duration: 0.9, ease: "back.out(1.2)" }, 35.96);
      tl.to("#r2", { borderColor: "#22c55e", duration: 0.2 }, 35.96);
      tl.fromTo("#ar2", { x: -30, opacity: 0 }, { x: 0, opacity: 1, duration: 0.25 }, 38.6);
      tl.fromTo("#bd2", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)" }, 38.9);
      tl.to("#s4", { opacity: 0, duration: 0.25 }, 39.3);

      /* ---------- S5 CTA ---------- */
      tl.fromTo("#t5a .titlebox", { scale: 0.5, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2.2)" }, 39.6);
      tl.to("#t5a", { opacity: 0, y: -30, duration: 0.18 }, 42.9);
      tl.fromTo("#ctaForm", { opacity: 0 }, { opacity: 1, duration: 0.05 }, 43.0);
      tl.fromTo("#ctaForm .banner", { scale: 0.3, rotation: -8 }, { scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2.5)" }, 43.0);
      tl.fromTo("#ctaArrow", { y: -20 }, { y: 14, duration: 0.35, yoyo: true, repeat: 11, ease: "sine.inOut" }, 43.3);
      tl.fromTo("#ctaForm .note", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: E }, 45.1);
      tl.to("#ctaForm", { opacity: 0, duration: 0.15 }, 47.2);

      /* ---------- END ---------- */
      tl.fromTo("#endCard", { opacity: 0 }, { opacity: 1, duration: 0.15 }, 47.25);
      tl.fromTo("#endCard .car", { x: -80, scale: 1.05 }, { x: 40, scale: 1.0, duration: 2.8, ease: "sine.out" }, 47.25);
      tl.fromTo("#e1", { y: -20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3 }, 47.35);
      tl.fromTo("#e2", { scale: 2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2)" }, 47.4);
      tl.fromTo("#e3", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3 }, 47.75);
      tl.fromTo("#e4", { scale: 0.5, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.5)" }, 48.25);
      tl.to("#e4", { scale: 1.06, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }, 48.6);

      /* ---------- captions ---------- */
{{CAPTION_JS}}

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
