from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd


def render_aggrid(
    df: pd.DataFrame,
    height: int = 300,
    page_size: int = 15,
    theme: str = "fresh",
):
    """
    Render a user-friendly AgGrid with sensible defaults.
    Only the DataFrame is required.
    """

    gb = GridOptionsBuilder.from_dataframe(df)

    # Default column behavior
    gb.configure_default_column(
                sortable=True,
                filter=True,
                resizable=True,
                minWidth=120
            )
    
    gb.configure_grid_options(
        enableQuickFilter=True, 
        domLayout="normal",
        # These two lines enable the ability to highlight and copy text
        enableCellTextSelection=True, 
        ensureDomOrder=True
    )

    # Pagination
    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=page_size
    )

    # Sidebar & quick filter
    gb.configure_side_bar()
    gb.configure_grid_options(
        enableQuickFilter=True,
        domLayout="normal"
    )

    grid_options = gb.build()

    return AgGrid(
        df,
        gridOptions=grid_options,
        theme=theme,
        height=height,
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.NO_UPDATE,
        allow_unsafe_jscode=False
    )
