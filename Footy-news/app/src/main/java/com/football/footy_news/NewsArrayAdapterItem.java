package com.football.footy_news;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.widget.ArrayAdapter;
import android.view.View;
import android.view.ViewGroup;
import android.view.LayoutInflater;
import android.app.Activity;
import android.widget.ImageView;
import android.widget.TextView;

import com.squareup.picasso.Picasso;

/**
 * Created by akshaykulkarni on 1/3/16.
 */
public class NewsArrayAdapterItem extends ArrayAdapter<NewsNode>
{
    Context             mContext;
    int                 layoutResourceId;
    NewsNode            data[] = null;

    public NewsArrayAdapterItem(Context mContext, int layoutResourceId, NewsNode[] data)
    {
        super(mContext, layoutResourceId, data);
        this.layoutResourceId   = layoutResourceId;
        this.mContext           = mContext;
        this.data               = data;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent)
    {
        if (convertView == null) {
            LayoutInflater inflater = ((Activity) mContext).getLayoutInflater();
            convertView = inflater.inflate(layoutResourceId, parent, false);
        }

        final NewsNode objectItem       = data[position];
        ImageView articleImage          = (ImageView) convertView.findViewById(R.id.news_image);
        Picasso.with(mContext).load(objectItem.image).into(articleImage);

        TextView title                  = (TextView) convertView.findViewById(R.id.title);
        title.setText(objectItem.title);

        convertView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                footyUtils.log(objectItem.newsId);
                Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(objectItem.href));
                mContext.startActivity(browserIntent);
            }
        });

        return convertView;
    }
}
