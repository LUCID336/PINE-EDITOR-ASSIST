"""Rebuild manually curated discovery indices. No scraped documentation or signature assertions."""
from pathlib import Path
import csv
root=Path(__file__).resolve().parents[1]
base='https://www.tradingview.com/pine-script-docs/'
groups={
'Welcome':'Welcome to Pine Script v6',
'Primer':'First steps|First indicator|Next steps',
'Language':'Execution model|Type system|Script structure|Identifiers|Declaration statements|Variable declarations|Operators|Conditional structures|Loops|Built-ins|User-defined functions|Objects|Enums|Methods|Arrays|Matrices|Maps',
'Visuals':'Overview|Backgrounds|Bar coloring|Bar plotting|Colors|Fills|Levels|Lines and boxes|Plots|Tables|Text and shapes',
'Concepts':'Alerts|Bar states|Chart information|Inputs|Libraries|Non-standard charts data|Other timeframes and data|Repainting|Sessions|Strategies|Strings|Time|Timeframes',
'Writing scripts':'Style guide|Debugging|Profiling and optimization|Publishing scripts|Limitations',
'Errors and warnings':'Overview|CE10101|CE10117|CW10003|CW10026|RE10139|RE10143',
'FAQ':'General|Alerts|Data structures|Functions|Indicators|Other data and timeframes|Programming|Strategies|Strings and formatting|Techniques|Times, dates, and sessions|Variables and operators|Visuals',
'Release notes':'Release notes',
'Migration guides':'Overview|To Pine Script version 6|To Pine Script version 5|To Pine Script version 4|To Pine Script version 3|To Pine Script version 2',
'More information':'Where can I get more information?'}
verified={'Welcome to Pine Script v6','Execution model','Type system','Script structure','Built-ins','Plots','Alerts','Inputs','Other timeframes and data','Repainting','Strategies','Publishing scripts','Limitations','Release notes','To Pine Script version 6','To Pine Script version 5','To Pine Script version 4','To Pine Script version 3','To Pine Script version 2'}
with (root/'references/manual-index.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f); w.writerow(['id','section','chapter','navigation_source','status']); i=0
 for group, chapters in groups.items():
  for chapter in chapters.split('|'):
   w.writerow([f'M{i:02}',group,chapter,base+'welcome/','TOPIC_SOURCE_LOCATED_NOT_FULL_READ' if chapter in verified and group != 'FAQ' else 'TOC_ONLY']); i+=1
assert i==78, i
# Names only; check exact availability, spelling, overloads, and semantics before use.
ns={
'global':'indicator strategy library import export plot plotshape plotchar plotarrow plotbar plotcandle hline fill bgcolor barcolor alert alertcondition na nz fixnan time time_close timestamp year month dayofmonth dayofweek hour minute second runtime.error open high low close volume hl2 hlc3 ohlc4 hlcc4 bar_index last_bar_index last_bar_time timenow bid ask',
' ta':'sma ema rma wma vwma swma alma hma linreg atr tr rsi roc mom macd stoch cci mfi dmi adx? supertrend bb bbw kc kcw donchian? highest lowest highestbars lowestbars pivothigh pivotlow crossover crossunder cross change rising falling barssince valuewhen cum correlation stdev variance dev median mode range percentile_linear_interpolation percentile_nearest_rank percentrank vwap vwap? obv pvt accdist wad wvad iii nvi pvi tsi cog sar highest lowest cmo rci willr? wpr max min sma',
'math':'abs acos asin atan avg ceil cos exp floor log log10 max min pow random round round_to_mintick sign sin sqrt sum tan todegrees toradians pi e phi rphi',
'str':'contains endswith format format_time length lower match pos repeat replace replace_all split startswith substring tonumber tostring trim upper',
'array':'new from copy size get set push pop shift unshift insert remove clear concat slice join sort sort_indices reverse includes indexof lastindexof binary_search binary_search_leftmost binary_search_rightmost first last min max sum avg median mode stdev variance covariance percentrank percentile_linear_interpolation percentile_nearest_rank range standardize fill every some abs',
'matrix':'new get set rows columns elements_count add_row add_col remove_row remove_col row col fill copy submatrix reshape swap_rows swap_columns sort transpose sum diff mult det inv pinv rank trace pow eigenvalues eigenvectors avg max min median mode is_square is_symmetric is_diagonal is_identity is_zero is_triangular is_stochastic is_antysymmetric?',
'map':'new put put_all get remove contains keys values size clear copy',
'request':'security security_lower_tf currency_rate financial economic dividends splits earnings seed footprint',
'footprint':'delta total_volume buy_volume sell_volume rows poc vah val',
'volume_row':'up_price down_price total_volume buy_volume sell_volume delta has_buy_imbalance has_sell_imbalance',
'input':'int float bool string color source timeframe symbol session time price text_area enum',
'line':'new delete copy get_x1 get_x2 get_y1 get_y2 get_price set_x1 set_x2 set_y1 set_y2 set_xy1 set_xy2 set_color set_extend set_style set_width set_xloc all',
'box':'new delete copy get_left get_right get_top get_bottom set_left set_right set_top set_bottom set_bgcolor set_border_color set_border_style set_border_width set_text set_text_color set_text_size set_text_halign set_text_valign all',
'label':'new delete copy get_x get_y get_text set_x set_y set_xy set_text set_color set_textcolor set_style set_size set_tooltip set_textalign set_xloc set_yloc all',
'polyline':'new delete all', 'linefill':'new delete get_line1 get_line2 set_color all',
'chart.point':'new now from_time from_index copy',
'table':'new cell clear delete merge_cells set_position set_bgcolor set_border_color set_border_width set_frame_color set_frame_width cell_set_text cell_set_bgcolor cell_set_text_color cell_set_text_size cell_set_text_halign cell_set_text_valign cell_set_width cell_set_height all',
'color':'new rgb r g b t from_gradient aqua black blue fuchsia gray green lime maroon navy olive orange purple red silver teal white yellow',
'barstate':'isfirst islast isnew isconfirmed ishistory isrealtime islastconfirmedhistory',
'syminfo':'ticker tickerid main_tickerid prefix root type description currency basecurrency mintick minmove pricescale pointvalue timezone session volumetype mincontract',
'chart':'is_standard is_heikinashi is_kagi is_linebreak is_pnf is_range is_renko left_visible_bar_time right_visible_bar_time bg_color fg_color',
 'timeframe':'period main_period multiplier in_seconds from_seconds change isintraday isdaily isweekly ismonthly isdwm isminutes isseconds isticks',
'session':'ismarket ispremarket ispostmarket isfirstbar islastbar isfirstbar_regular islastbar_regular',
'ticker':'new modify standard inherit heikinashi renko linebreak kagi pointfigure',
'strategy':'entry order exit close close_all cancel cancel_all position_size position_avg_price equity netprofit grossprofit grossloss openprofit max_drawdown max_runup wintrades losstrades eventrades opentrades closedtrades initial_capital convert_to_account convert_to_symbol default_entry_qty margin_liquidation_price long short',
'strategy.risk':'allow_entry_in max_drawdown max_cons_loss_days max_intraday_filled_orders max_intraday_loss max_position_size',
'strategy.closedtrades':'entry_id entry_price entry_time entry_bar_index exit_id exit_price exit_time exit_bar_index size profit profit_percent commission max_drawdown max_runup first_index',
'strategy.opentrades':'entry_id entry_price entry_time entry_bar_index size profit profit_percent commission max_drawdown max_runup',
'log':'info warning error',
'barmerge':'gaps_on gaps_off lookahead_on lookahead_off',
'display':'all none pane price_scale status_line data_window',
'alert':'freq_all freq_once_per_bar freq_once_per_bar_close',
'format':'mintick price volume percent',
'position':'top_left top_center top_right middle_left middle_center middle_right bottom_left bottom_center bottom_right',
'plot':'style_line style_linebr style_stepline style_histogram style_cross style_area style_columns style_circles',
'extend':'none left right both','xloc':'bar_index bar_time','yloc':'price abovebar belowbar','size':'auto tiny small normal large huge','shape':'arrowup arrowdown circle cross diamond flag labelup labeldown square triangleup triangledown xcross','location':'abovebar belowbar top bottom absolute','text':'align_left align_center align_right align_top align_bottom',
}
with (root/'references/symbol-catalog.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f); w.writerow(['namespace','symbol','reference_lookup','status']); seen=set()
 for n, items in ns.items():
  n=n.strip()
  for item in items.split():
   if '?' in item: continue
   name=item if n=='global' else n+'.'+item
   if name in seen: continue
   seen.add(name); w.writerow([n,name,'https://www.tradingview.com/pine-script-reference/v6/','CANDIDATE_VERIFY_EXACT_ENTRY'])
print('Manual topics:',i,'; discovery symbols:',len(seen))
