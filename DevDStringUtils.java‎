package com.ngage.integration.util;

import org.apache.commons.lang3.StringUtils;

import java.security.MessageDigest;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DevDStringUtils {

    static String issueIdRegEx = "([a-zA-Z0-9]+-[0-9]+)|[#(/]?([0-9]{4,6})[/)]?";
    static String bitbucketEmailIdRegEx = "\\<(.*?)\\>";
    static Pattern p = Pattern.compile(issueIdRegEx);
    static Pattern pbb = Pattern.compile(bitbucketEmailIdRegEx);

    public static boolean constantTimeCompare(String a, String b) {
        return MessageDigest.isEqual(a.getBytes(), b.getBytes());
    }

    public static String getIssue(String summary, String description, String sourceBranch, String targetBranch) {
        String[] fields = {summary, description, sourceBranch, targetBranch};

        for (String field : fields) {
            if (isIssuePresent(field)) {
                return extractIssue(field);
            }
        }
        return org.apache.commons.lang3.StringUtils.EMPTY;
    }

    private static boolean isIssuePresent(String field) {
        return StringUtils.isNotBlank(field) && p.matcher(field).find();
    }

    public static String extractIssue(String field) {
        if (StringUtils.isNotBlank(field)) {
            Matcher m = p.matcher(field);
            if (m.find()) {
                return m.group();
            }
        }
        return org.apache.commons.lang3.StringUtils.EMPTY;
    }

    public static String getBitBucketUserEmail(String raw) {
        Matcher m = pbb.matcher(raw);
        String issue = org.apache.commons.lang3.StringUtils.EMPTY;
        while (m.find()) {
            issue = m.group(1);
        }
        return issue;
    }
}
