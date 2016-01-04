package com.football.footy_news;

/**
 * Created by akshaykulkarni on 1/3/16.
 */

import java.util.ArrayList;
public class NewsNode
{
    public String title;
    public String image;
    public String href;
    public String source;
    public ArrayList other;

    public NewsNode(String title,String image,String href,String source,ArrayList other)
    {
        this.title  = title;
        this.image  = image;
        this.href   = href;
        this.source = source;
        this.other  = new ArrayList();
    }
}