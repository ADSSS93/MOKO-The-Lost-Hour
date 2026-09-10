import pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text()

needle = 'static int death_rewind_tick=0;'
replacement = needle + 'static uint16_t temporal_pickup_mask=0;static int temporal_pickup_notice=0,temporal_pickup_kind=0;'
if needle not in src: raise SystemExit('temporal pickup globals anchor missing')
src = src.replace(needle, replacement, 1)

needle = 'death_rewind_tick=0;'
replacement = needle + 'temporal_pickup_mask=0;temporal_pickup_notice=0;temporal_pickup_kind=0;'
if needle not in src: raise SystemExit('temporal pickup reset anchor missing')
src = src.replace(needle, replacement, 1)

anchor = 'static int warden_phase_level(void)'
helpers = r'''static void temporal_pickups(void){
    int i,id,x,y,p;
    if(room>3)return;
    for(i=0;i<3;i++){
        id=room*3+i;
        if(temporal_pickup_mask&(1u<<id))continue;
        x=52+((room*61+i*83)%225);
        y=92+((room*37+i*41)%91);
        p=1+((anim_tick/7+i)&3);
        /* Three distinct low-poly/pixel-art time relics. */
        if(i==0){
            rect(x-p,y-p,8+p*2,8+p*2,38,72,105);
            rect(x,y,8,8,105,225,245);rect(x+3,y-4,2,16,220,250,255);
        }else if(i==1){
            rect(x-p,y-p,10+p*2,10+p*2,65,27,90);
            rect(x,y,10,10,150,70,205);rect(x+3,y+3,4,4,235,185,255);
        }else{
            rect(x-p,y-p,10+p*2,10+p*2,90,52,18);
            rect(x,y,10,10,225,156,55);rect(x+2,y+2,6,6,255,225,120);
        }
        if(hit(px,py,12,18,x-7,y-7,24,24)){
            temporal_pickup_mask|=(1u<<id);temporal_pickup_kind=i;temporal_pickup_notice=90;
            if(i==0){timer_frames+=60*5;if(timer_frames>60*60*5)timer_frames=60*60*5;gameplay_reward(&gameplay,25);score+=25;}
            else if(i==1){gameplay.focus+=25;if(gameplay.focus>100)gameplay.focus=100;gameplay_reward(&gameplay,20);score+=20;}
            else{if(health<3)health++;else{gameplay_reward(&gameplay,40);score+=40;}}
            sfx(i==0?0x2450:(i==1?0x2550:0x2650));
        }
    }
    if(temporal_pickup_notice>0){
        temporal_pickup_notice--;
        rect(px-4,py-5,20,3,115+(temporal_pickup_kind*40),85,190);
        if(temporal_pickup_kind==0)FntPrint(font_id,"\nTIME FRAGMENT +5 SEC");
        else if(temporal_pickup_kind==1)FntPrint(font_id,"\nFOCUS CRYSTAL +25");
        else FntPrint(font_id,"\nCLOCK HEART RESTORED");
    }
}
'''
if anchor not in src: raise SystemExit('temporal pickup helper anchor missing')
src = src.replace(anchor, helpers + anchor, 1)

needle = 'world_event_art();echo_art();'
replacement = 'world_event_art();echo_art();temporal_pickups();'
if needle not in src: raise SystemExit('temporal pickup room anchor missing')
src = src.replace(needle, replacement, 1)

src = src.replace('REWIND REV 261','PICKUP REV 262',1)
src = src.replace('R261 %02d:%02d','P262 %02d:%02d',1)

pathlib.Path(sys.argv[2]).write_text(src)
