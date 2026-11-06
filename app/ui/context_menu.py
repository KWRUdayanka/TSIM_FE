# ui/context_menu.py
import streamlit as st
import streamlit.components.v1 as components


def inject_right_click_handler():
    """
    Injects a JS snippet that intercepts right-click on any element
    with a data-symbol attribute and navigates to ?ctx=<symbol>.
    """
    components.html(
        """
        <script>
        (function() {
            const doc = window.parent.document;

            doc.addEventListener('contextmenu', function(e) {
                const target = e.target.closest('[data-symbol]');
                if (!target) return;
                e.preventDefault();

                const symbol = target.getAttribute('data-symbol');
                if (!symbol) return;

                const url = new URL(window.parent.location.href);
                url.searchParams.set('ctx', symbol);
                window.parent.location.href = url.toString();
            });
        })();
        </script>
        """,
        height=0,
    )


def consume_context_click(state):
    """
    Called once per rerun. If ?ctx=<symbol> is present in the URL,
    pull it into state and clear the param so it doesn't persist.
    """
    ctx = st.query_params.get("ctx")
    if ctx:
        state.context_symbol = ctx
        state.context_open = True
        del st.query_params["ctx"]