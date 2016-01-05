package com.football.footy_news.footy_news;

/**
 * Created by akshaykulkarni on 1/4/16.
 */
import android.util.Pair;

import com.loopj.android.http.JsonHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import org.apache.http.Header;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.security.MessageDigest;
import java.util.ArrayList;

public class footyUtils {
    private static footyUtils ourInstance   = new footyUtils();
    public static String hashKey            = "5Tde@7Wn$";

    public static footyUtils getInstance()
    {
        return ourInstance;
    }

    private footyUtils() {
    }

    public static String md5(String input)
    {
        try
        {
            MessageDigest md = MessageDigest.getInstance("MD5");
            md.update(input.getBytes());
            byte byteData[] = md.digest();
            StringBuffer sb = new StringBuffer();
            for (int i = 0; i < byteData.length; i++)
                sb.append(Integer.toString((byteData[i] & 0xff) + 0x100, 16).substring(1));
            StringBuffer hexString = new StringBuffer();
            for (int i=0;i<byteData.length;i++) {
                String hex=Integer.toHexString(0xff & byteData[i]);
                if(hex.length()==1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        }
        catch (Exception e)
        {

        }
        return "";
    }

    public static void log(int news_id)
    {
        RequestParams params = new RequestParams();
        params.add("id",Integer.toString(news_id));
        params.add("hash",md5(Integer.toString(news_id).concat(hashKey)));
        RestClient.post("log", params, new JsonHttpResponseHandler()
        {
            @Override
            public void onSuccess(int statusCode, Header[] headers, JSONObject response)
            {
            }

            @Override
            public void onFailure(int statusCode, Header[] headers, Throwable e, JSONObject response)
            {
            }

        });
    }

    public static NewsNode [] constructNews(JSONObject response)
    {
        NewsNode[] allNews = null;
        try
        {
            JSONArray result    = response.getJSONArray("result");
            int totalNewsItem   = result.length();
            allNews             = new NewsNode[totalNewsItem];

            for (int i = 0; i < totalNewsItem; i++) {
                JSONObject newsItem = result.getJSONObject(i);
                int newsId          = newsItem.getInt("id");
                String source       = newsItem.getString("source");
                String image        = newsItem.getString("image");
                String href         = newsItem.getString("href");
                String title        = newsItem.getString("title");
                JSONArray similar   = newsItem.getJSONArray("other");

                ArrayList other = new ArrayList();
                for (int j = 0; j < similar.length(); j++) {
                    JSONObject newsObject = similar.getJSONObject(j);
                    Pair newsPair = new Pair<>(newsObject.getString("href"), newsObject.getString("title"));
                    other.add(newsPair);
                }
                allNews[i] = new NewsNode(newsId, title, image, href, source, other);
            }
        }
        catch (JSONException e)
        {
        }
        return allNews;
    }
}
