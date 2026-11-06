# ui/order_book.py
import streamlit as st
from state import SharedState
from config import DEPTH


def render_order_book(state: SharedState, sym: str):
    st.markdown(
        f'<div class="book-header" data-symbol="{sym}" '
        f'style="cursor: context-menu;">{sym}</div>',
        unsafe_allow_html=True,
    )

    book, _ = state.snapshot(sym)      # my_orders no longer needed
    bids = book["bids"][:DEPTH]
    asks = book["asks"][:DEPTH]

    if bids and asks:
        spread = asks[0]["price"] - bids[0]["price"]
        st.markdown(f'<span class="spread">SPREAD {spread:.3f}</span>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<span class="spread">NO BOOK</span>', unsafe_allow_html=True)

    h1, h2, h3, h4 = st.columns(4)
    h1.markdown('<div class="col-header">Bid Qty</div>', unsafe_allow_html=True)
    h2.markdown('<div class="col-header" style="text-align:right;">Bid</div>', unsafe_allow_html=True)
    h3.markdown('<div class="col-header">Ask</div>', unsafe_allow_html=True)
    h4.markdown('<div class="col-header" style="text-align:right;">Ask Qty</div>', unsafe_allow_html=True)

    all_q = [float(b.get("qty") or 0) for b in bids] + \
            [float(a.get("qty") or 0) for a in asks]
    max_q = max(all_q) if all_q else 1.0

    rows = max(len(bids), len(asks))
    for i in range(rows):
        b = bids[i] if i < len(bids) else {}
        a = asks[i] if i < len(asks) else {}

        b_px, a_px = b.get("price"), a.get("price")
        b_key = f"{float(b_px):.2f}" if b_px is not None else None
        a_key = f"{float(a_px):.2f}" if a_px is not None else None
        b_qty = int(b["qty"]) if b.get("qty") is not None else 0
        a_qty = int(a["qty"]) if a.get("qty") is not None else 0
        b_pct = (b_qty / max_q) * 100 if max_q else 0
        a_pct = (a_qty / max_q) * 100 if max_q else 0

        # --- side-aware ownership check ---
        b_owned = state.has_order_at(sym, b_key, "1")   # BUY
        a_owned = state.has_order_at(sym, a_key, "2")   # SELL
        b_cls = "my-order" if b_owned else "bid"
        a_cls = "my-order" if a_owned else "ask"

        c1, c2, c3, c4 = st.columns(4)

        c1.markdown(
            f'<div style="position:relative;padding:2px 0;">'
            f'<div style="position:absolute;left:0;top:0;bottom:0;width:{b_pct}%;'
            f'background:linear-gradient(90deg,'
            f'rgba(74,222,128,0.55) 0%,'
            f'rgba(74,222,128,0.25) 60%,'
            f'rgba(74,222,128,0.10) 100%);'
            f'border-radius:2px;"></div>'
            f'<div class="{b_cls}" style="position:relative;z-index:1;'
            f'padding-left:4px;">'
            f'{"● " if b_owned else ""}{b_qty:,}</div></div>',
            unsafe_allow_html=True,
        )
        c2.markdown(
            f'<div class="{b_cls}" style="text-align:right;">'
            f'{f"{b_px:.2f}" if b_px else "—"}</div>',
            unsafe_allow_html=True,
        )
        c3.markdown(
            f'<div class="{a_cls}">{f"{a_px:.2f}" if a_px else "—"}</div>',
            unsafe_allow_html=True,
        )
        c4.markdown(
            f'<div style="position:relative;padding:2px 0;">'
            f'<div style="position:absolute;right:0;top:0;bottom:0;width:{a_pct}%;'
            f'background:linear-gradient(270deg,'
            f'rgba(248,113,113,0.55) 0%,'
            f'rgba(248,113,113,0.25) 60%,'
            f'rgba(248,113,113,0.10) 100%);'
            f'border-radius:2px;"></div>'
            f'<div class="{a_cls}" style="position:relative;z-index:1;'
            f'text-align:right;padding-right:4px;">'
            f'{a_qty:,}{" ●" if a_owned else ""}</div></div>',
            unsafe_allow_html=True,
        )