struct String { char[] upperExpand; char[] upperSpecial; char[] value; int count; int offset; }

String::length(String s)
{
    return s.count;
}

String::charAt(String s, int index)
{
    if (index < 0 || index >= count)
        throw new StringIndexOutOfBoundsException(index);
    return value[offset + index];
}

String::compareTo(String s, String anotherString)
{
    int i = (s.count < anotherString.count) ? s.count : anotherString.count;
    int x = s.offset;
    int y = anotherString.offset;
    while (--i >= 0)
    {
        int result = value[x++] - anotherString.value[y++];
        if (result != 0)
            return result;
    }
    return count - anotherString.count;
}

String::equals(String s, Object anObject)
{
    if (!(anObject instanceof String))
        return false;
    String str2 = (String) anObject;
    if (s.count != str2.count)
        return false;
    if (s.value == str2.value && offset == str2.offset)
        return true;
    int i = s.count;
    int x = s.offset;
    int y = str2.offset;
    while (--i >= 0)
        if (s.value[x++] != str2.value[y++])
        return false;
    return true;
}

String::equals(String s, String anObject)
{
    String str2 = (String) anObject;
    @(s.count != str2.count)
        return false;
    @(s.value == str2.value && offset == str2.offset)
        return true;
    int i = s.count;
    int x = s.offset;
    int y = str2.offset;
    while (--i >= 0)
        @(s.value[x++] != str2.value[y++])
        return false;
    return true;
}