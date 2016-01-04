package com.football.footy_news;

import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.ListView;

import com.loopj.android.http.JsonHttpResponseHandler;
import org.apache.http.Header;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.util.ArrayList;
import android.util.Pair;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        RestClient.get("", null, new JsonHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, JSONObject response) {
                try {
                    JSONArray result = response.getJSONArray("result");
                    int totalNewsItem = result.length();
                    NewsNode[] allNews = new NewsNode[totalNewsItem];

                    for (int i = 0; i < totalNewsItem; i++) {
                        JSONObject newsItem = result.getJSONObject(i);
                        int newsId      = newsItem.getInt("id");
                        String source   = newsItem.getString("source");
                        String image    = newsItem.getString("image");
                        String href     = newsItem.getString("href");
                        String title    = newsItem.getString("title");
                        JSONArray similar = newsItem.getJSONArray("other");

                        ArrayList other = new ArrayList();
                        for (int j = 0; j < similar.length(); j++) {
                            JSONObject newsObject = similar.getJSONObject(j);
                            Pair newsPair = new Pair<>(newsObject.getString("href"), newsObject.getString("title"));
                            other.add(newsPair);
                        }
                        allNews[i] = new NewsNode(newsId,title, image, href, source, other);
                    }
                    loadNews(allNews);
                } catch (JSONException e) {
                }
            }

            @Override
            public void onFailure(int statusCode, Header[] headers, Throwable e, JSONObject response) {
            }
        });
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    private void loadNews(NewsNode [] news)
    {
        NewsArrayAdapterItem adapter    = new NewsArrayAdapterItem(this, R.layout.news_node, news);
        ListView listViewViewItems      = (ListView) findViewById(R.id.newsListView);
        listViewViewItems.setAdapter(adapter);
    }
}
