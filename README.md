This is a simple utility that will compress Xmind files, which can get very large if you do a lot of screen shots or insert pictures into your mind map.
It preserves readability by compressing Xmind files by as much as 95%.

xmind_compress.py — usage examples:                                           
                                                                                
  # Single file → creates test-workbook-compressed.xmind                        
  xmind_compress.py notes.xmind                                              
                                                                                
  # Multiple files (shell expands wildcard)                                     
  xmind_compress.py *.xmind                                                     
                                                                                
  # Quoted wildcard (script expands it)                                         
  xmind_compress.py "*.xmind"                                                   
                                                                                
  # Custom output name                                                          
  xmind_compress.py notes.xmind --output notes-small.xmind                      
                                                                                
  # Overwrite original                                                       
  xmind_compress.py notes.xmind --in-place
                                                                                
  # Tune quality/size tradeoff (higher quality, larger output)                  
  xmind_compress.py notes.xmind --quality 85 --max-dim 1920                     
                                                                                
  # See per-image stats                                                         
  xmind_compress.py notes.xmind --verbose
                                                                                
  Options:                                                                   

  ┌─────────────────┬─────────────┬────────────────────────────────┐
  │      Flag       │   Default   │          Description           │
  ├─────────────────┼─────────────┼────────────────────────────────┤
  │ -o / --output   │ —           │ Output path (single file only) │
  ├─────────────────┼─────────────┼────────────────────────────────┤
  │ -i / --in-place │ —           │ Overwrite original             │            
  ├─────────────────┼─────────────┼────────────────────────────────┤            
  │ -s / --suffix   │ -compressed │ Suffix for output filename     │            
  ├─────────────────┼─────────────┼────────────────────────────────┤            
  │ -q / --quality  │ 80          │ JPEG quality (1–95)            │         
  ├─────────────────┼─────────────┼────────────────────────────────┤            
  │ -d / --max-dim  │ 1440        │ Max image dimension in pixels  │
  ├─────────────────┼─────────────┼────────────────────────────────┤            
  │ -v / --verbose  │ —           │ Per-image size details         │         
  └─────────────────┴─────────────┴────────────────────────────────┘            
   
  If you want to call it as just xmind_compress from anywhere, you can symlink  
  it into your PATH:
  
  ln -s /Users/{user name}/{pick a directory}/xmind_compress.py /usr/local/bin/xmind_compress   

